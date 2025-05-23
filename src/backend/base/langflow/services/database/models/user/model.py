from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.api_key import ApiKey
    from langflow.services.database.models.flow import Flow
    from langflow.services.database.models.folder import Folder
    from langflow.services.database.models.variable import Variable
    from langflow.services.database.models.workspace import Workspace, WorkspaceMember
    from langflow.services.database.models.crm.client import Client
    from langflow.services.database.models.crm.invoice import Invoice
    from langflow.services.database.models.crm.opportunity import Opportunity
    from langflow.services.database.models.crm.task import Task
    from langflow.services.database.models.book import Book, BookTemplate


class UserOptin(BaseModel):
    github_starred: bool = Field(default=False)
    dialog_dismissed: bool = Field(default=False)
    discord_clicked: bool = Field(default=False)
    # Add more opt-in actions as needed


class User(SQLModel, table=True):  # type: ignore[call-arg]
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    username: str = Field(index=True, unique=True)
    password: str = Field()
    profile_image: str | None = Field(default=None, nullable=True)
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    create_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login_at: datetime | None = Field(default=None, nullable=True)
    # Supabase Auth integration
    supabase_user_id: str | None = Field(default=None, nullable=True, index=True)
    api_keys: list["ApiKey"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    store_api_key: str | None = Field(default=None, nullable=True)
    flows: list["Flow"] = Relationship(back_populates="user")
    variables: list["Variable"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    folders: list["Folder"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    # Workspace relationships
    owned_workspaces: list["Workspace"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    workspace_memberships: list["WorkspaceMember"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "delete"},
    )
    optins: dict[str, Any] | None = Field(
        sa_column=Column(JSON, default=lambda: UserOptin().model_dump(), nullable=True)
    )

    # CRM relationships
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

    # Book Creator relationships
    books: list["Book"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "delete"})
    book_templates: list["BookTemplate"] = Relationship(
        sa_relationship_kwargs={"primaryjoin": "User.id == BookTemplate.user_id", "cascade": "delete"}
    )


class UserCreate(SQLModel):
    username: str = Field()
    password: str = Field()
    optins: dict[str, Any] | None = Field(
        default={"github_starred": False, "dialog_dismissed": False, "discord_clicked": False}
    )


class UserRead(SQLModel):
    id: UUID = Field(default_factory=uuid4)
    username: str = Field()
    profile_image: str | None = Field()
    store_api_key: str | None = Field(nullable=True)
    is_active: bool = Field()
    is_superuser: bool = Field()
    create_at: datetime = Field()
    updated_at: datetime = Field()
    last_login_at: datetime | None = Field(nullable=True)
    supabase_user_id: str | None = Field(default=None, nullable=True)
    optins: dict[str, Any] | None = Field(default=None)


class UserUpdate(SQLModel):
    username: str | None = None
    profile_image: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    last_login_at: datetime | None = None
    supabase_user_id: str | None = None
    optins: dict[str, Any] | None = None
