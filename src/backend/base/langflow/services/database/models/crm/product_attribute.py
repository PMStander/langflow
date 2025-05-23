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


class ProductAttributeLink(SQLModel, table=True):  # type: ignore[call-arg]
    """Link table for many-to-many relationship between products and attributes."""
    __tablename__ = "product_attribute_link"

    product_id: UUIDstr = Field(
        foreign_key="product.id", primary_key=True
    )
    attribute_id: UUIDstr = Field(
        foreign_key="product_attribute.id", primary_key=True
    )


class ProductAttributeBase(SQLModel):
    """Base model for ProductAttribute."""
    name: str = Field(index=True)
    slug: str = Field(index=True)
    type: str = Field(default="select")  # select, text, etc.
    order_by: str = Field(default="menu_order")  # menu_order, name, name_num, id
    has_archives: bool = Field(default=False)


class ProductAttribute(ProductAttributeBase, table=True):  # type: ignore[call-arg]
    """ProductAttribute model for database."""
    __tablename__ = "product_attribute"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    workspace: "Workspace" = Relationship(back_populates="product_attributes")
    creator: "User" = Relationship(
        back_populates="created_product_attributes", 
        sa_relationship_kwargs={"foreign_keys": "ProductAttribute.created_by"}
    )
    
    # Many-to-many relationship with products
    products: List["Product"] = Relationship(
        back_populates="attributes",
        link_model=ProductAttributeLink
    )
    
    # One-to-many relationship with attribute terms
    terms: List["ProductAttributeTerm"] = Relationship(
        back_populates="attribute",
        sa_relationship_kwargs={"cascade": "delete"}
    )


class ProductAttributeCreate(ProductAttributeBase):
    """Schema for creating a product attribute."""
    workspace_id: UUIDstr


class ProductAttributeRead(ProductAttributeBase):
    """Schema for reading a product attribute."""
    id: UUIDstr
    workspace_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductAttributeUpdate(SQLModel):
    """Schema for updating a product attribute."""
    name: str | None = None
    slug: str | None = None
    type: str | None = None
    order_by: str | None = None
    has_archives: bool | None = None


class ProductAttributeTermBase(SQLModel):
    """Base model for ProductAttributeTerm."""
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    menu_order: int = Field(default=0)


class ProductAttributeTerm(ProductAttributeTermBase, table=True):  # type: ignore[call-arg]
    """ProductAttributeTerm model for database."""
    __tablename__ = "product_attribute_term"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    attribute_id: UUIDstr = Field(index=True, foreign_key="product_attribute.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    attribute: "ProductAttribute" = Relationship(back_populates="terms")


class ProductAttributeTermCreate(ProductAttributeTermBase):
    """Schema for creating a product attribute term."""
    attribute_id: UUIDstr


class ProductAttributeTermRead(ProductAttributeTermBase):
    """Schema for reading a product attribute term."""
    id: UUIDstr
    attribute_id: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductAttributeTermUpdate(SQLModel):
    """Schema for updating a product attribute term."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    menu_order: int | None = None
