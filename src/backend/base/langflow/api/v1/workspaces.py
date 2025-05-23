from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import (
    Workspace,
    WorkspaceCreate,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberRead,
    WorkspaceMemberUpdate,
    WorkspaceRead,
    WorkspaceUpdate,
)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=201)
async def create_workspace(
    *,
    session: DbSession,
    workspace: WorkspaceCreate,
    current_user: CurrentActiveUser,
):
    """Create a new workspace."""
    try:
        # Create the workspace
        db_workspace = Workspace(
            **workspace.model_dump(),
            owner_id=current_user.id,
        )
        session.add(db_workspace)
        await session.commit()
        await session.refresh(db_workspace)
        
        # Add the creator as an owner member
        workspace_member = WorkspaceMember(
            workspace_id=db_workspace.id,
            user_id=current_user.id,
            role="owner"
        )
        session.add(workspace_member)
        await session.commit()
        
        return db_workspace
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workspace with this name already exists",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=list[WorkspaceRead], status_code=200)
async def read_workspaces(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
):
    """Get all workspaces the user has access to."""
    try:
        # Get workspaces where user is owner or member
        workspaces = (
            await session.exec(
                select(Workspace)
                .where(
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).all()
        return workspaces
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{workspace_id}", response_model=WorkspaceRead, status_code=200)
async def read_workspace(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific workspace."""
    try:
        # Check if user has access to this workspace
        workspace_member = (
            await session.exec(
                select(WorkspaceMember)
                .where(
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.user_id == current_user.id
                )
            )
        ).first()
        
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        workspace_member != None  # noqa: E711
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        return workspace
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{workspace_id}", response_model=WorkspaceRead, status_code=200)
async def update_workspace(
    *,
    session: DbSession,
    workspace_id: UUID,
    workspace: WorkspaceUpdate,
    current_user: CurrentActiveUser,
):
    """Update a workspace."""
    try:
        # Check if user is the owner of the workspace
        db_workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first()
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to update it",
            )
        
        # Update workspace fields
        workspace_data = workspace.model_dump(exclude_unset=True)
        for key, value in workspace_data.items():
            setattr(db_workspace, key, value)
        
        await session.commit()
        await session.refresh(db_workspace)
        
        return db_workspace
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a workspace."""
    try:
        # Check if user is the owner of the workspace
        db_workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    Workspace.owner_id == current_user.id
                )
            )
        ).first()
        
        if not db_workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or you don't have permission to delete it",
            )
        
        # Delete workspace
        await session.delete(db_workspace)
        await session.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
