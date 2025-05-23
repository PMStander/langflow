from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import Text, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.crm.product import Product


class ProductVariationBase(SQLModel):
    """Base model for ProductVariation."""
    description: str | None = Field(default=None, sa_column=Column(Text))
    sku: str | None = Field(default=None, index=True)
    price: float = Field(default=0.0)
    regular_price: float = Field(default=0.0)
    sale_price: float | None = Field(default=None)
    on_sale: bool = Field(default=False)
    status: str = Field(default="publish", index=True)  # publish, private
    virtual: bool = Field(default=False)
    downloadable: bool = Field(default=False)
    downloads: List[Dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    download_limit: int | None = Field(default=-1)
    download_expiry: int | None = Field(default=-1)
    tax_status: str = Field(default="taxable")  # taxable, shipping, none
    tax_class: str | None = Field(default=None)
    manage_stock: bool = Field(default=False)
    stock_quantity: int | None = Field(default=None)
    stock_status: str = Field(default="instock")  # instock, outofstock, onbackorder
    backorders: str = Field(default="no")  # no, notify, yes
    backorders_allowed: bool = Field(default=False)
    backordered: bool = Field(default=False)
    weight: str | None = Field(default=None)
    dimensions: Dict[str, str] | None = Field(default=None, sa_column=Column(JSON))
    shipping_class: str | None = Field(default=None)
    shipping_class_id: int | None = Field(default=None)
    menu_order: int = Field(default=0)
    attributes: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    image: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class ProductVariation(ProductVariationBase, table=True):  # type: ignore[call-arg]
    """ProductVariation model for database."""
    __tablename__ = "product_variation"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    product_id: UUIDstr = Field(index=True, foreign_key="product.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product: "Product" = Relationship(back_populates="variations")


class ProductVariationCreate(ProductVariationBase):
    """Schema for creating a product variation."""
    product_id: UUIDstr


class ProductVariationRead(ProductVariationBase):
    """Schema for reading a product variation."""
    id: UUIDstr
    product_id: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductVariationUpdate(SQLModel):
    """Schema for updating a product variation."""
    description: str | None = None
    sku: str | None = None
    price: float | None = None
    regular_price: float | None = None
    sale_price: float | None = None
    on_sale: bool | None = None
    status: str | None = None
    virtual: bool | None = None
    downloadable: bool | None = None
    downloads: List[Dict[str, Any]] | None = None
    download_limit: int | None = None
    download_expiry: int | None = None
    tax_status: str | None = None
    tax_class: str | None = None
    manage_stock: bool | None = None
    stock_quantity: int | None = None
    stock_status: str | None = None
    backorders: str | None = None
    backorders_allowed: bool | None = None
    backordered: bool | None = None
    weight: str | None = None
    dimensions: Dict[str, str] | None = None
    shipping_class: str | None = None
    shipping_class_id: int | None = None
    menu_order: int | None = None
    attributes: Dict[str, Any] | None = None
    image: Dict[str, Any] | None = None
