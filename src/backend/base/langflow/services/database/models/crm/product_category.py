from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID, uuid4

from sqlalchemy import Text, Column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.workspace import Workspace
    from langflow.services.database.models.crm.product import Product


class ProductCategoryLink(SQLModel, table=True):  # type: ignore[call-arg]
    """Link table for many-to-many relationship between products and categories."""
    __tablename__ = "product_category_link"

    product_id: UUIDstr = Field(
        foreign_key="product.id", primary_key=True
    )
    category_id: UUIDstr = Field(
        foreign_key="product_category.id", primary_key=True
    )


class ProductCategoryBase(SQLModel):
    """Base model for ProductCategory."""
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    parent_id: UUIDstr | None = Field(default=None, foreign_key="product_category.id")
    display: str = Field(default="default")  # default, products, subcategories, both


class ProductCategory(ProductCategoryBase, table=True):  # type: ignore[call-arg]
    """ProductCategory model for database."""
    __tablename__ = "product_category"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    workspace: "Workspace" = Relationship(back_populates="product_categories")
    creator: "User" = Relationship(
        back_populates="created_product_categories",
        sa_relationship_kwargs={"foreign_keys": "ProductCategory.created_by"}
    )

    # Self-referential relationship for parent-child categories
    parent: Optional["ProductCategory"] = Relationship(
        back_populates="children",
        sa_relationship_kwargs={"remote_side": "ProductCategory.id"}
    )
    children: List["ProductCategory"] = Relationship(
        back_populates="parent"
    )

    # Many-to-many relationship with products (temporarily disabled)
    # products: List["Product"] = Relationship(
    #     back_populates="categories",
    #     link_model=ProductCategoryLink
    # )


class ProductCategoryCreate(ProductCategoryBase):
    """Schema for creating a product category."""
    workspace_id: UUIDstr


class ProductCategoryRead(ProductCategoryBase):
    """Schema for reading a product category."""
    id: UUIDstr
    workspace_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductCategoryUpdate(SQLModel):
    """Schema for updating a product category."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    parent_id: UUIDstr | None = None
    display: str | None = None
