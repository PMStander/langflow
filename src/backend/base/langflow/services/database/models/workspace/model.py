from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.folder import Folder
    from langflow.services.database.models.user import User
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity
    from langflow.services.database.models.crm.task import Task
    from langflow.services.database.models.crm.product import Product
    from langflow.services.database.models.crm.product_category import ProductCategory
    from langflow.services.database.models.crm.product_attribute import ProductAttribute


class WorkspaceBase(SQLModel):
    """Base model for Workspace."""
    name: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))


class Workspace(WorkspaceBase, table=True):  # type: ignore[call-arg]
    """Workspace model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    owner_id: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    owner: "User" = Relationship(back_populates="owned_workspaces")
    folders: list["Folder"] = Relationship(back_populates="workspace")
    members: list["WorkspaceMember"] = Relationship(back_populates="workspace")

    # CRM relationships
    clients: list["Client"] = Relationship(back_populates="workspace")
    invoices: list["Invoice"] = Relationship(back_populates="workspace")
    opportunities: list["Opportunity"] = Relationship(back_populates="workspace")
    tasks: list["Task"] = Relationship(back_populates="workspace")
    products: list["Product"] = Relationship(back_populates="workspace")
    product_categories: list["ProductCategory"] = Relationship(back_populates="workspace")
    product_attributes: list["ProductAttribute"] = Relationship(back_populates="workspace")

    __table_args__ = (UniqueConstraint("owner_id", "name", name="unique_workspace_name"),)


class WorkspaceMember(SQLModel, table=True):  # type: ignore[call-arg]
    """WorkspaceMember model for database."""
    __tablename__ = "workspace_member"

    workspace_id: UUIDstr = Field(foreign_key="workspace.id", primary_key=True)
    user_id: UUIDstr = Field(foreign_key="user.id", primary_key=True)
    role: str = Field(default="viewer")  # Options: owner, editor, viewer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace: "Workspace" = Relationship(back_populates="members")
    user: "User" = Relationship(back_populates="workspace_memberships")


class WorkspaceCreate(WorkspaceBase):
    """Model for creating a new workspace."""
    pass


class WorkspaceRead(WorkspaceBase):
    """Model for reading a workspace."""
    id: UUIDstr
    owner_id: UUIDstr
    created_at: datetime
    updated_at: datetime


class WorkspaceUpdate(SQLModel):
    """Model for updating a workspace."""
    name: str | None = None
    description: str | None = None


class WorkspaceMemberCreate(SQLModel):
    """Model for creating a new workspace member."""
    workspace_id: UUIDstr
    user_id: UUIDstr
    role: str = "viewer"


class WorkspaceMemberRead(SQLModel):
    """Model for reading a workspace member."""
    workspace_id: UUIDstr
    user_id: UUIDstr
    role: str
    created_at: datetime


class WorkspaceMemberUpdate(SQLModel):
    """Model for updating a workspace member."""
    role: str | None = None
