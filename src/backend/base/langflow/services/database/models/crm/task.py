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
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity


class TaskBase(SQLModel):
    """Base model for Task."""
    title: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="open")  # open, in_progress, completed, cancelled
    priority: str = Field(default="medium")  # low, medium, high
    due_date: datetime | None = Field(default=None)


class Task(TaskBase, table=True):  # type: ignore[call-arg]
    """Task model for database."""
    __tablename__ = "task"

    id: UUIDstr = Field(
        default_factory=uuid4,
        primary_key=True,
        unique=True,
        sa_column=Column(PostgresUUID(as_uuid=True), unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    assigned_to: UUIDstr | None = Field(default=None, foreign_key="user.id")
    client_id: UUIDstr | None = Field(default=None, foreign_key="client.id")
    invoice_id: UUIDstr | None = Field(default=None, foreign_key="invoice.id")
    opportunity_id: UUIDstr | None = Field(default=None, foreign_key="opportunity.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace: "Workspace" = Relationship(back_populates="tasks")
    creator: "User" = Relationship(back_populates="created_tasks", sa_relationship_kwargs={"foreign_keys": "Task.created_by"})
    assignee: "User" = Relationship(back_populates="assigned_tasks", sa_relationship_kwargs={"foreign_keys": "Task.assigned_to"})
    client: "Client" = Relationship(back_populates="tasks")
    invoice: "Invoice" = Relationship(back_populates="tasks")
    opportunity: "Opportunity" = Relationship(back_populates="tasks")


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    workspace_id: UUIDstr
    assigned_to: UUIDstr | None = None
    client_id: UUIDstr | None = None
    invoice_id: UUIDstr | None = None
    opportunity_id: UUIDstr | None = None


class TaskRead(TaskBase):
    """Model for reading a task."""
    id: UUIDstr
    workspace_id: UUIDstr
    created_by: UUIDstr
    assigned_to: UUIDstr | None
    client_id: UUIDstr | None
    invoice_id: UUIDstr | None
    opportunity_id: UUIDstr | None
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    """Model for updating a task."""
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: datetime | None = None
    assigned_to: UUIDstr | None = None
    client_id: UUIDstr | None = None
    invoice_id: UUIDstr | None = None
    opportunity_id: UUIDstr | None = None
