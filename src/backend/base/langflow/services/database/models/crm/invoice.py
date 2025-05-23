from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, Column
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.workspace import Workspace
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.task import Task


class InvoiceBase(SQLModel):
    """Base model for Invoice."""
    invoice_number: str = Field(index=True)
    amount: float = Field()
    status: str = Field(default="draft")  # draft, sent, paid, overdue
    issue_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    due_date: datetime | None = Field(default=None)
    description: str | None = Field(default=None, sa_column=Column(Text))


class Invoice(InvoiceBase, table=True):  # type: ignore[call-arg]
    """Invoice model for database."""
    __tablename__ = "invoice"
    
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    client_id: UUIDstr = Field(index=True, foreign_key="client.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    workspace: "Workspace" = Relationship(back_populates="invoices")
    client: "Client" = Relationship(back_populates="invoices")
    creator: "User" = Relationship(back_populates="created_invoices", sa_relationship_kwargs={"foreign_keys": [created_by]})
    tasks: list["Task"] = Relationship(back_populates="invoice", sa_relationship_kwargs={"cascade": "delete"})


class InvoiceCreate(InvoiceBase):
    """Model for creating a new invoice."""
    workspace_id: UUIDstr
    client_id: UUIDstr


class InvoiceRead(InvoiceBase):
    """Model for reading an invoice."""
    id: UUIDstr
    workspace_id: UUIDstr
    client_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class InvoiceUpdate(SQLModel):
    """Model for updating an invoice."""
    invoice_number: str | None = None
    amount: float | None = None
    status: str | None = None
    issue_date: datetime | None = None
    due_date: datetime | None = None
    description: str | None = None
