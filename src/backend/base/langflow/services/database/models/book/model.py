from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, JSON, Text
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.workspace import Workspace


class BookBase(SQLModel):
    """Base model for Book."""
    name: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    book_type: str = Field(index=True)  # low-content, journal, planner, etc.
    dimensions: dict = Field(sa_column=Column(JSON))  # width, height, units
    page_count: int = Field(default=100)


class Book(BookBase, table=True):  # type: ignore[call-arg]
    """Book model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    user_id: UUIDstr = Field(index=True, foreign_key="user.id")
    workspace_id: UUIDstr | None = Field(index=True, foreign_key="workspace.id", nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user: "User" = Relationship(back_populates="books")
    workspace: "Workspace" = Relationship(back_populates="books")
    cover: "BookCover" = Relationship(back_populates="book", sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"})
    interior: "BookInterior" = Relationship(back_populates="book", sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"})
    pages: list["BookPage"] = Relationship(back_populates="book", sa_relationship_kwargs={"cascade": "all, delete, delete-orphan"})


class BookCover(SQLModel, table=True):  # type: ignore[call-arg]
    """BookCover model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    book_id: UUIDstr = Field(foreign_key="book.id", unique=True)
    front_design: dict = Field(sa_column=Column(JSON))  # Design elements for front cover
    back_design: dict = Field(sa_column=Column(JSON))  # Design elements for back cover
    spine_design: dict = Field(sa_column=Column(JSON))  # Design elements for spine
    
    # Relationship
    book: "Book" = Relationship(back_populates="cover")


class BookInterior(SQLModel, table=True):  # type: ignore[call-arg]
    """BookInterior model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    book_id: UUIDstr = Field(foreign_key="book.id", unique=True)
    template_id: UUIDstr | None = Field(foreign_key="book_template.id", nullable=True)
    layout_settings: dict = Field(sa_column=Column(JSON))  # Margins, headers, footers, etc.
    
    # Relationships
    book: "Book" = Relationship(back_populates="interior")
    template: "BookTemplate" = Relationship()


class BookPage(SQLModel, table=True):  # type: ignore[call-arg]
    """BookPage model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    book_id: UUIDstr = Field(foreign_key="book.id", index=True)
    page_number: int = Field(index=True)
    content: dict = Field(sa_column=Column(JSON))  # Page content and design elements
    template_id: UUIDstr | None = Field(foreign_key="book_template.id", nullable=True)
    
    # Relationships
    book: "Book" = Relationship(back_populates="pages")
    template: "BookTemplate" = Relationship()


class BookTemplate(SQLModel, table=True):  # type: ignore[call-arg]
    """BookTemplate model for database."""
    id: UUIDstr = Field(default_factory=uuid4, primary_key=True, unique=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None)
    category: str = Field(index=True)  # cover, interior, page
    template_type: str = Field(index=True)  # lined, grid, dot, blank, etc.
    is_system: bool = Field(default=False)  # System-provided or user-created
    user_id: UUIDstr | None = Field(foreign_key="user.id", nullable=True)
    content: dict = Field(sa_column=Column(JSON))  # Template definition
    
    # Relationship
    user: "User" = Relationship()


# Pydantic models for API
class BookCreate(BookBase):
    """Model for creating a new book."""
    workspace_id: UUIDstr | None = None


class BookRead(BookBase):
    """Model for reading a book."""
    id: UUIDstr
    user_id: UUIDstr
    workspace_id: UUIDstr | None
    created_at: datetime
    updated_at: datetime


class BookUpdate(SQLModel):
    """Model for updating a book."""
    name: str | None = None
    description: str | None = None
    book_type: str | None = None
    dimensions: dict | None = None
    page_count: int | None = None
    workspace_id: UUIDstr | None = None


class BookCoverCreate(SQLModel):
    """Model for creating a new book cover."""
    book_id: UUIDstr
    front_design: dict
    back_design: dict
    spine_design: dict


class BookCoverRead(SQLModel):
    """Model for reading a book cover."""
    id: UUIDstr
    book_id: UUIDstr
    front_design: dict
    back_design: dict
    spine_design: dict


class BookCoverUpdate(SQLModel):
    """Model for updating a book cover."""
    front_design: dict | None = None
    back_design: dict | None = None
    spine_design: dict | None = None


class BookInteriorCreate(SQLModel):
    """Model for creating a new book interior."""
    book_id: UUIDstr
    template_id: UUIDstr | None = None
    layout_settings: dict


class BookInteriorRead(SQLModel):
    """Model for reading a book interior."""
    id: UUIDstr
    book_id: UUIDstr
    template_id: UUIDstr | None
    layout_settings: dict


class BookInteriorUpdate(SQLModel):
    """Model for updating a book interior."""
    template_id: UUIDstr | None = None
    layout_settings: dict | None = None


class BookPageCreate(SQLModel):
    """Model for creating a new book page."""
    book_id: UUIDstr
    page_number: int
    content: dict
    template_id: UUIDstr | None = None


class BookPageRead(SQLModel):
    """Model for reading a book page."""
    id: UUIDstr
    book_id: UUIDstr
    page_number: int
    content: dict
    template_id: UUIDstr | None


class BookPageUpdate(SQLModel):
    """Model for updating a book page."""
    page_number: int | None = None
    content: dict | None = None
    template_id: UUIDstr | None = None


class BookTemplateCreate(SQLModel):
    """Model for creating a new book template."""
    name: str
    description: str | None = None
    category: str
    template_type: str
    is_system: bool = False
    content: dict


class BookTemplateRead(SQLModel):
    """Model for reading a book template."""
    id: UUIDstr
    name: str
    description: str | None
    category: str
    template_type: str
    is_system: bool
    user_id: UUIDstr | None
    content: dict


class BookTemplateUpdate(SQLModel):
    """Model for updating a book template."""
    name: str | None = None
    description: str | None = None
    category: str | None = None
    template_type: str | None = None
    content: dict | None = None
