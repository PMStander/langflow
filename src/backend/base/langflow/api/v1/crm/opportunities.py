from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityRead,
    OpportunityUpdate,
)
from langflow.services.database.models.workspace import Workspace, WorkspaceMember

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.post("/", response_model=OpportunityRead, status_code=201)
async def create_opportunity(
    *,
    session: DbSession,
    opportunity: OpportunityCreate,
    current_user: CurrentActiveUser,
):
    """Create a new opportunity."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == opportunity.workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to create opportunities in it",
            )
        
        # Create the opportunity
        db_opportunity = Opportunity(
            **opportunity.model_dump(),
            created_by=current_user.id,
        )
        session.add(db_opportunity)
        await session.commit()
        await session.refresh(db_opportunity)
        return db_opportunity
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create opportunity: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[OpportunityRead], status_code=200)
async def read_opportunities(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    status: str | None = None,
):
    """Get all opportunities the user has access to."""
    try:
        # Base query to get opportunities from workspaces the user has access to
        query = (
            select(Opportunity)
            .where(
                or_(
                    Opportunity.workspace_id.in_(
                        select(Workspace.id)
                        .where(Workspace.owner_id == current_user.id)
                    ),
                    Opportunity.workspace_id.in_(
                        select(WorkspaceMember.workspace_id)
                        .where(WorkspaceMember.user_id == current_user.id)
                    )
                )
            )
        )
        
        # Add filters if provided
        if workspace_id:
            query = query.where(Opportunity.workspace_id == workspace_id)
        
        if client_id:
            query = query.where(Opportunity.client_id == client_id)
        
        if status:
            query = query.where(Opportunity.status == status)
        
        # Execute query
        opportunities = (await session.exec(query)).all()
        return opportunities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{opportunity_id}", response_model=OpportunityRead, status_code=200)
async def read_opportunity(
    *,
    session: DbSession,
    opportunity_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific opportunity."""
    try:
        # Check if user has access to the opportunity's workspace
        opportunity = (
            await session.exec(
                select(Opportunity)
                .where(
                    Opportunity.id == opportunity_id,
                    or_(
                        Opportunity.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Opportunity.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or access denied",
            )
        
        return opportunity
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{opportunity_id}", response_model=OpportunityRead, status_code=200)
async def update_opportunity(
    *,
    session: DbSession,
    opportunity_id: UUID,
    opportunity: OpportunityUpdate,
    current_user: CurrentActiveUser,
):
    """Update an opportunity."""
    try:
        # Check if user has access to update the opportunity
        db_opportunity = (
            await session.exec(
                select(Opportunity)
                .where(
                    Opportunity.id == opportunity_id,
                    or_(
                        Opportunity.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Opportunity.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role.in_(["owner", "editor"])
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not db_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or you don't have permission to update it",
            )
        
        # Update opportunity fields
        opportunity_data = opportunity.model_dump(exclude_unset=True)
        for key, value in opportunity_data.items():
            setattr(db_opportunity, key, value)
        
        # Update the updated_at timestamp
        from datetime import datetime, timezone
        db_opportunity.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(db_opportunity)
        return db_opportunity
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{opportunity_id}", status_code=204)
async def delete_opportunity(
    *,
    session: DbSession,
    opportunity_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete an opportunity."""
    try:
        # Check if user has access to delete the opportunity
        db_opportunity = (
            await session.exec(
                select(Opportunity)
                .where(
                    Opportunity.id == opportunity_id,
                    or_(
                        Opportunity.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Opportunity.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(
                                WorkspaceMember.user_id == current_user.id,
                                WorkspaceMember.role == "owner"
                            )
                        )
                    )
                )
            )
        ).first()
        
        if not db_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found or you don't have permission to delete it",
            )
        
        await session.delete(db_opportunity)
        await session.commit()
        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
