from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.client import (
    Client,
    ClientCreate,
    ClientRead,
    ClientUpdate,
)
from langflow.services.database.models.workspace import Workspace, WorkspaceMember

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
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == client.workspace_id,
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
                detail="Workspace not found or you don't have permission to create clients in it",
            )
        
        # Create the client
        db_client = Client(
            **client.model_dump(),
            created_by=current_user.id,
        )
        session.add(db_client)
        await session.commit()
        await session.refresh(db_client)
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


@router.get("/", response_model=list[ClientRead], status_code=200)
async def read_clients(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    status: str | None = None,
):
    """Get all clients the user has access to."""
    try:
        # Base query to get clients from workspaces the user has access to
        query = (
            select(Client)
            .where(
                or_(
                    Client.workspace_id.in_(
                        select(Workspace.id)
                        .where(Workspace.owner_id == current_user.id)
                    ),
                    Client.workspace_id.in_(
                        select(WorkspaceMember.workspace_id)
                        .where(WorkspaceMember.user_id == current_user.id)
                    )
                )
            )
        )
        
        # Add filters if provided
        if workspace_id:
            query = query.where(Client.workspace_id == workspace_id)
        
        if status:
            query = query.where(Client.status == status)
        
        # Execute query
        clients = (await session.exec(query)).all()
        return clients
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
                    or_(
                        Client.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Client.workspace_id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
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
        # Check if user has access to update the client
        db_client = (
            await session.exec(
                select(Client)
                .where(
                    Client.id == client_id,
                    or_(
                        Client.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Client.workspace_id.in_(
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
        
        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or you don't have permission to update it",
            )
        
        # Update client fields
        client_data = client.model_dump(exclude_unset=True)
        for key, value in client_data.items():
            setattr(db_client, key, value)
        
        # Update the updated_at timestamp
        from datetime import datetime, timezone
        db_client.updated_at = datetime.now(timezone.utc)
        
        await session.commit()
        await session.refresh(db_client)
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
        # Check if user has access to delete the client
        db_client = (
            await session.exec(
                select(Client)
                .where(
                    Client.id == client_id,
                    or_(
                        Client.workspace_id.in_(
                            select(Workspace.id)
                            .where(Workspace.owner_id == current_user.id)
                        ),
                        Client.workspace_id.in_(
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
        
        if not db_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found or you don't have permission to delete it",
            )
        
        await session.delete(db_client)
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
