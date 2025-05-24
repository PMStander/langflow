from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.client import (
    Client,
    ClientCreate,
    ClientRead,
    ClientUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("/", response_model=ClientRead, status_code=201)
async def create_client(
    *,
    session: DbSession,
    client: ClientCreate,
    current_user: CurrentActiveUser,
):
    """Create a new client."""
    try:
        # Check if user has access to the workspace with edit permission
        await check_workspace_access(
            session,
            client.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Create the client
        db_client = Client(
            **client.model_dump(),
            created_by=current_user.id,
        )
        # Update timestamps
        update_entity_timestamps(db_client, is_new=True)
        session.add(db_client)
        await session.commit()
        await session.refresh(db_client)

        # Invalidate dashboard cache since client data has changed
        invalidate_cache("get_workspace_stats")
        invalidate_cache("get_client_distribution")
        invalidate_cache("get_recent_activity")

        return db_client
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create client: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/", response_model=PaginatedResponse[ClientRead], status_code=200)
async def read_clients(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    client_status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    page: int | None = None,
):
    """
    Get all clients the user has access to.

    Supports pagination with skip/limit or page/limit parameters.
    Returns a paginated response with items and metadata.
    """
    try:
        # Base query to get clients from workspaces the user has access to
        query = (
            select(Client)
            .where(get_entity_access_filter(Client, current_user.id))
        )

        # Add filters if provided
        if workspace_id:
            query = query.where(Client.workspace_id == workspace_id)

        if client_status:
            query = query.where(Client.status == client_status)

        # Apply pagination and get items with metadata
        clients, metadata = await paginate_query(
            session=session,
            query=query,
            skip=skip,
            limit=limit,
            page=page
        )

        # Return paginated response
        return PaginatedResponse(items=clients, metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{client_id}", response_model=ClientRead, status_code=200)
async def read_client(
    *,
    session: DbSession,
    client_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific client."""
    try:
        # Check if user has access to the client's workspace
        client = (
            await session.exec(
                select(Client)
                .where(
                    Client.id == client_id,
                    get_entity_access_filter(Client, current_user.id)
                )
            )
        ).first()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or access denied",
            )

        return client
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{client_id}", response_model=ClientRead, status_code=200)
async def update_client(
    *,
    session: DbSession,
    client_id: UUID,
    client: ClientUpdate,
    current_user: CurrentActiveUser,
):
    """Update a client."""
    try:
        # Check if client exists
        db_client = (
            await session.exec(
                select(Client)
                .where(Client.id == client_id)
            )
        ).first()

        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        # Check if user has edit permission for the client's workspace
        await check_workspace_access(
            session,
            db_client.workspace_id,
            current_user,
            require_edit_permission=True
        )

        # Update client fields and timestamps
        client_data = client.model_dump(exclude_unset=True)
        update_entity_timestamps(db_client, update_data=client_data)

        await session.commit()
        await session.refresh(db_client)

        # Invalidate dashboard cache since client data has changed
        invalidate_cache("get_workspace_stats")
        invalidate_cache("get_client_distribution")

        return db_client
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    *,
    session: DbSession,
    client_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a client."""
    try:
        # Check if client exists
        db_client = (
            await session.exec(
                select(Client)
                .where(Client.id == client_id)
            )
        ).first()

        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found",
            )

        # Check if user has owner permission for the client's workspace
        await check_workspace_access(
            session,
            db_client.workspace_id,
            current_user,
            require_owner_permission=True
        )

        await session.delete(db_client)
        await session.commit()

        # Invalidate dashboard cache since client data has changed
        invalidate_cache("get_workspace_stats")
        invalidate_cache("get_client_distribution")
        invalidate_cache("get_recent_activity")

        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
