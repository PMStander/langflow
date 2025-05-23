from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, Column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
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

    id: UUIDstr = Field(
        default_factory=uuid4,
        primary_key=True,
        unique=True,
        sa_column=Column(PostgresUUID(as_uuid=True), unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace: "Workspace" = Relationship(back_populates="clients")
    creator: "User" = Relationship(back_populates="created_clients", sa_relationship_kwargs={"foreign_keys": "Client.created_by"})
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
