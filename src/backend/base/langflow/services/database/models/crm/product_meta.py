from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, Any
from uuid import UUID, uuid4

from sqlalchemy import Text, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.crm.product import Product


class ProductMetaBase(SQLModel):
    """Base model for ProductMeta."""
    key: str = Field(index=True)
    value: Any = Field(default=None, sa_column=Column(JSON))


class ProductMeta(ProductMetaBase, table=True):  # type: ignore[call-arg]
    """ProductMeta model for database."""
    __tablename__ = "product_meta"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    product_id: UUIDstr = Field(index=True, foreign_key="product.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships (temporarily disabled)
    # product: "Product" = Relationship(back_populates="meta_data")


class ProductMetaCreate(ProductMetaBase):
    """Schema for creating a product meta."""
    product_id: UUIDstr


class ProductMetaRead(ProductMetaBase):
    """Schema for reading a product meta."""
    id: UUIDstr
    product_id: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductMetaUpdate(SQLModel):
    """Schema for updating a product meta."""
    key: str | None = None
    value: Any | None = None
