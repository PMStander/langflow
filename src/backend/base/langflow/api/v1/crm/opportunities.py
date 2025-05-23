from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.opportunity import (
    Opportunity,
    OpportunityCreate,
    OpportunityRead,
    OpportunityUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse

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
        # Check if user has access to the workspace with edit permission
        await check_workspace_access(
            session,
            opportunity.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Create the opportunity
        db_opportunity = Opportunity(
            **opportunity.model_dump(),
            created_by=current_user.id,
        )
        # Update timestamps
        update_entity_timestamps(db_opportunity, is_new=True)
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


@router.get("/", response_model=PaginatedResponse[OpportunityRead], status_code=200)
async def read_opportunities(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_id: UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    page: int | None = None,
):
    """
    Get all opportunities the user has access to.

    Supports pagination with skip/limit or page/limit parameters.
    Returns a paginated response with items and metadata.
    """
    try:
        # Base query to get opportunities from workspaces the user has access to
        query = (
            select(Opportunity)
            .where(get_entity_access_filter(Opportunity, current_user.id))
        )

        # Add filters if provided
        if workspace_id:
            query = query.where(Opportunity.workspace_id == workspace_id)

        if client_id:
            query = query.where(Opportunity.client_id == client_id)

        if status:
            query = query.where(Opportunity.status == status)

        # Apply pagination and get items with metadata
        opportunities, metadata = await paginate_query(
            session=session,
            query=query,
            skip=skip,
            limit=limit,
            page=page
        )

        # Return paginated response
        return PaginatedResponse(items=opportunities, metadata=metadata)
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
        # Check if opportunity exists and user has access to it
        opportunity = (
            await session.exec(
                select(Opportunity)
                .where(
                    Opportunity.id == opportunity_id,
                    get_entity_access_filter(Opportunity, current_user.id)
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
        # Check if opportunity exists
        db_opportunity = (
            await session.exec(
                select(Opportunity)
                .where(Opportunity.id == opportunity_id)
            )
        ).first()

        if not db_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found",
            )

        # Check if user has edit permission for the opportunity's workspace
        await check_workspace_access(
            session,
            db_opportunity.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Update opportunity fields and timestamps
        opportunity_data = opportunity.model_dump(exclude_unset=True)
        update_entity_timestamps(db_opportunity, update_data=opportunity_data)

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
        # Check if opportunity exists
        db_opportunity = (
            await session.exec(
                select(Opportunity)
                .where(Opportunity.id == opportunity_id)
            )
        ).first()

        if not db_opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found",
            )

        # Check if user has owner permission for the opportunity's workspace
        await check_workspace_access(
            session,
            db_opportunity.workspace_id,
            current_user,
            require_owner_permission=True
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
