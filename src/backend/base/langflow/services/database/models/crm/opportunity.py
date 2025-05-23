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
    from langflow.services.database.models.crm.task import Task


class OpportunityBase(SQLModel):
    """Base model for Opportunity."""
    name: str = Field(index=True)
    value: float | None = Field(default=None)
    status: str = Field(default="new", index=True)  # new, qualified, proposal, negotiation, won, lost
    description: str | None = Field(default=None, sa_column=Column(Text))
    expected_close_date: datetime | None = Field(default=None, index=True)


class Opportunity(OpportunityBase, table=True):  # type: ignore[call-arg]
    """Opportunity model for database."""
    __tablename__ = "opportunity"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    client_id: UUIDstr = Field(index=True, foreign_key="client.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace: "Workspace" = Relationship(back_populates="opportunities")
    client: "Client" = Relationship(back_populates="opportunities")
    creator: "User" = Relationship(back_populates="created_opportunities", sa_relationship_kwargs={"foreign_keys": "Opportunity.created_by"})
    tasks: list["Task"] = Relationship(back_populates="opportunity", sa_relationship_kwargs={"cascade": "delete"})


class OpportunityCreate(OpportunityBase):
    """Model for creating a new opportunity."""
    workspace_id: UUIDstr
    client_id: UUIDstr


class OpportunityRead(OpportunityBase):
    """Model for reading an opportunity."""
    id: UUIDstr
    workspace_id: UUIDstr
    client_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class OpportunityUpdate(SQLModel):
    """Model for updating an opportunity."""
    name: str | None = None
    value: float | None = None
    status: str | None = None
    description: str | None = None
    expected_close_date: datetime | None = None
