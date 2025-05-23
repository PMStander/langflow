from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Text, UniqueConstraint
from sqlmodel import Column, Field, Relationship, SQLModel

from langflow.services.database.models.flow.model import Flow, FlowRead
from langflow.services.database.models.user.model import User

if TYPE_CHECKING:
    from langflow.services.database.models.workspace import Workspace


class FolderBase(SQLModel):
    name: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))


class Folder(FolderBase, table=True):  # type: ignore[call-arg]
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    parent_id: UUID | None = Field(default=None, foreign_key="folder.id")

    parent: Optional["Folder"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "Folder.id"},
    )
    children: list["Folder"] = Relationship(back_populates="parent")
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    user: User = Relationship(back_populates="folders")
    workspace_id: UUID | None = Field(default=None, foreign_key="workspace.id", nullable=True, index=True)
    workspace: Optional["Workspace"] = Relationship(back_populates="folders")
    flows: list[Flow] = Relationship(
        back_populates="folder", sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"}
    )

    __table_args__ = (UniqueConstraint("user_id", "name", "workspace_id", name="unique_folder_name_per_workspace"),)


class FolderCreate(FolderBase):
    components_list: list[UUID] | None = None
    flows_list: list[UUID] | None = None
    workspace_id: UUID | None = None


class FolderRead(FolderBase):
    id: UUID
    parent_id: UUID | None = Field()
    workspace_id: UUID | None = Field()


class FolderReadWithFlows(FolderBase):
    id: UUID
    parent_id: UUID | None = Field()
    workspace_id: UUID | None = Field()
    flows: list[FlowRead] = Field(default=[])


class FolderUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
    parent_id: UUID | None = None
    workspace_id: UUID | None = None
    components: list[UUID] = Field(default_factory=list)
    flows: list[UUID] = Field(default_factory=list)
