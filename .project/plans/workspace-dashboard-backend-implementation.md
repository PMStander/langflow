# Workspace Dashboard & CRM Backend Implementation Plan

## Database Schema Implementation

### 1. Create New Database Models

#### File: `src/backend/base/langflow/services/database/models/crm/__init__.py`
```python
from .client import Client, ClientBase, ClientCreate, ClientRead, ClientUpdate
from .invoice import Invoice, InvoiceBase, InvoiceCreate, InvoiceRead, InvoiceUpdate
from .opportunity import Opportunity, OpportunityBase, OpportunityCreate, OpportunityRead, OpportunityUpdate
from .task import Task, TaskBase, TaskCreate, TaskRead, TaskUpdate

__all__ = [
    "Client",
    "ClientBase",
    "ClientCreate",
    "ClientRead",
    "ClientUpdate",
    "Invoice",
    "InvoiceBase",
    "InvoiceCreate",
    "InvoiceRead",
    "InvoiceUpdate",
    "Opportunity",
    "OpportunityBase",
    "OpportunityCreate",
    "OpportunityRead",
    "OpportunityUpdate",
    "Task",
    "TaskBase",
    "TaskCreate",
    "TaskRead",
    "TaskUpdate",
]
```

#### File: `src/backend/base/langflow/services/database/models/crm/client.py`
```python
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, Column
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.workspace import Workspace
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity
    from langflow.services.database.models.crm.task import Task


class ClientBase(SQLModel):
    """Base model for Client."""
    name: str = Field(index=True)
    email: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    company: str | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="active")  # active, inactive, lead


class Client(ClientBase, table=True):  # type: ignore[call-arg]
    """Client model for database."""
    __tablename__ = "client"
    
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    workspace: "Workspace" = Relationship(back_populates="clients")
    creator: "User" = Relationship(back_populates="created_clients", sa_relationship_kwargs={"foreign_keys": [created_by]})
    invoices: list["Invoice"] = Relationship(back_populates="client", sa_relationship_kwargs={"cascade": "delete"})
    opportunities: list["Opportunity"] = Relationship(back_populates="client", sa_relationship_kwargs={"cascade": "delete"})
    tasks: list["Task"] = Relationship(back_populates="client", sa_relationship_kwargs={"cascade": "delete"})


class ClientCreate(ClientBase):
    """Model for creating a new client."""
    workspace_id: UUIDstr


class ClientRead(ClientBase):
    """Model for reading a client."""
    id: UUIDstr
    workspace_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class ClientUpdate(SQLModel):
    """Model for updating a client."""
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company: str | None = None
    description: str | None = None
    status: str | None = None
```

Similar model files would be created for Invoice, Opportunity, and Task.

### 2. Update Existing Models

#### File: `src/backend/base/langflow/services/database/models/workspace/model.py`
```python
# Add to the imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity
    from langflow.services.database.models.crm.task import Task

# Add to the Workspace class
class Workspace(WorkspaceBase, table=True):
    # Existing fields and relationships...
    
    # New relationships
    clients: list["Client"] = Relationship(back_populates="workspace")
    invoices: list["Invoice"] = Relationship(back_populates="workspace")
    opportunities: list["Opportunity"] = Relationship(back_populates="workspace")
    tasks: list["Task"] = Relationship(back_populates="workspace")
```

#### File: `src/backend/base/langflow/services/database/models/user/model.py`
```python
# Add to the imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity
    from langflow.services.database.models.crm.task import Task

# Add to the User class
class User(SQLModel, table=True):
    # Existing fields and relationships...
    
    # New relationships
    created_clients: list["Client"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Client.created_by", "cascade": "delete"},
    )
    created_invoices: list["Invoice"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Invoice.created_by", "cascade": "delete"},
    )
    created_opportunities: list["Opportunity"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Opportunity.created_by", "cascade": "delete"},
    )
    created_tasks: list["Task"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"foreign_keys": "Task.created_by", "cascade": "delete"},
    )
    assigned_tasks: list["Task"] = Relationship(
        back_populates="assignee",
        sa_relationship_kwargs={"foreign_keys": "Task.assigned_to", "cascade": "delete"},
    )
```

### 3. Create Database Migration Script

#### File: `src/backend/base/langflow/alembic/versions/crm_tables_migration.py`
```python
"""Create CRM tables

Revision ID: crm_tables_migration
Revises: [previous_migration_id]
Create Date: 2025-05-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql
from uuid import uuid4

# revision identifiers, used by Alembic.
revision = 'crm_tables_migration'
down_revision = '[previous_migration_id]'
branch_labels = None
depends_on = None


def upgrade():
    # Create client table
    op.create_table(
        'client',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='active'),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.id'), index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create invoice table
    op.create_table(
        'invoice',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('invoice_number', sa.String(), nullable=False, index=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, default='draft'),
        sa.Column('issue_date', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.id'), index=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('client.id'), index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create opportunity table
    op.create_table(
        'opportunity',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='new'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('expected_close_date', sa.DateTime(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.id'), index=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('client.id'), index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create task table
    op.create_table(
        'task',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid4),
        sa.Column('title', sa.String(), nullable=False, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, default='open'),
        sa.Column('priority', sa.String(), nullable=False, default='medium'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('workspace.id'), index=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), index=True),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('client.id'), nullable=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoice.id'), nullable=True),
        sa.Column('opportunity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('opportunity.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )


def downgrade():
    op.drop_table('task')
    op.drop_table('opportunity')
    op.drop_table('invoice')
    op.drop_table('client')
```

## API Endpoint Implementation

### 1. Create API Routers

#### File: `src/backend/base/langflow/api/v1/clients.py`
```python
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
```

Similar API router files would be created for Invoices, Opportunities, and Tasks.

### 2. Create Dashboard API Endpoints

#### File: `src/backend/base/langflow/api/v1/dashboard.py`
```python
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlmodel import select, or_

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.workspace import Workspace, WorkspaceMember
from langflow.services.database.models.crm.client import Client
from langflow.services.database.models.crm.invoice import Invoice
from langflow.services.database.models.crm.opportunity import Opportunity
from langflow.services.database.models.crm.task import Task

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/workspace/{workspace_id}/stats", status_code=200)
async def get_workspace_stats(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get statistics for a specific workspace."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get client count
        client_count = (
            await session.exec(
                select(func.count())
                .where(Client.workspace_id == workspace_id)
            )
        ).one()
        
        # Get active client count
        active_client_count = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "active"
                )
            )
        ).one()
        
        # Get invoice count
        invoice_count = (
            await session.exec(
                select(func.count())
                .where(Invoice.workspace_id == workspace_id)
            )
        ).one()
        
        # Get total revenue (sum of paid invoices)
        total_revenue = (
            await session.exec(
                select(func.sum(Invoice.amount))
                .where(
                    Invoice.workspace_id == workspace_id,
                    Invoice.status == "paid"
                )
            )
        ).one() or 0
        
        # Get opportunity count
        opportunity_count = (
            await session.exec(
                select(func.count())
                .where(Opportunity.workspace_id == workspace_id)
            )
        ).one()
        
        # Get open opportunity value
        open_opportunity_value = (
            await session.exec(
                select(func.sum(Opportunity.value))
                .where(
                    Opportunity.workspace_id == workspace_id,
                    Opportunity.status.in_(["new", "qualified", "proposal", "negotiation"])
                )
            )
        ).one() or 0
        
        # Get task count by status
        open_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "open"
                )
            )
        ).one()
        
        in_progress_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "in_progress"
                )
            )
        ).one()
        
        completed_tasks = (
            await session.exec(
                select(func.count())
                .where(
                    Task.workspace_id == workspace_id,
                    Task.status == "completed"
                )
            )
        ).one()
        
        return {
            "clients": {
                "total": client_count,
                "active": active_client_count,
            },
            "invoices": {
                "total": invoice_count,
                "revenue": total_revenue,
            },
            "opportunities": {
                "total": opportunity_count,
                "open_value": open_opportunity_value,
            },
            "tasks": {
                "open": open_tasks,
                "in_progress": in_progress_tasks,
                "completed": completed_tasks,
            }
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/workspace/{workspace_id}/client-distribution", status_code=200)
async def get_client_distribution(
    *,
    session: DbSession,
    workspace_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get client distribution by status for a specific workspace."""
    try:
        # Check if user has access to the workspace
        workspace = (
            await session.exec(
                select(Workspace)
                .where(
                    Workspace.id == workspace_id,
                    or_(
                        Workspace.owner_id == current_user.id,
                        Workspace.id.in_(
                            select(WorkspaceMember.workspace_id)
                            .where(WorkspaceMember.user_id == current_user.id)
                        )
                    )
                )
            )
        ).first()
        
        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )
        
        # Get client count by status
        active_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "active"
                )
            )
        ).one()
        
        inactive_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "inactive"
                )
            )
        ).one()
        
        lead_clients = (
            await session.exec(
                select(func.count())
                .where(
                    Client.workspace_id == workspace_id,
                    Client.status == "lead"
                )
            )
        ).one()
        
        return {
            "active": active_clients,
            "inactive": inactive_clients,
            "lead": lead_clients,
        }
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
```

### 3. Update Main Router Configuration

#### File: `src/backend/base/langflow/api/router.py`
```python
# Add to the imports
from langflow.api.v1 import clients, invoices, opportunities, tasks, dashboard

# Add to the v1_router.include_router calls
v1_router.include_router(clients.router)
v1_router.include_router(invoices.router)
v1_router.include_router(opportunities.router)
v1_router.include_router(tasks.router)
v1_router.include_router(dashboard.router)
```

This backend implementation plan provides a solid foundation for the CRM and Dashboard features, with proper database models, API endpoints, and security considerations.
