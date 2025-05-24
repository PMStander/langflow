from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Dict, Any
from uuid import uuid4

from sqlalchemy import Text, Column, JSON
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr
from langflow.services.database.models.crm.product_category import ProductCategoryLink
from langflow.services.database.models.crm.product_attribute import ProductAttributeLink

if TYPE_CHECKING:
    from langflow.services.database.models.workspace.model import Workspace
    from langflow.services.database.models.user import User
    from langflow.services.database.models.crm.product_category import ProductCategory
    from langflow.services.database.models.crm.product_attribute import ProductAttribute
    from langflow.services.database.models.crm.product_variation import ProductVariation
    from langflow.services.database.models.crm.product_meta import ProductMeta
    from langflow.services.database.models.crm.product_review import ProductReview


class ProductBase(SQLModel):
    """Base model for Product."""
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: str | None = Field(default=None, sa_column=Column(Text))
    short_description: str | None = Field(default=None)
    sku: str | None = Field(default=None, index=True)
    price: float = Field(default=0.0)
    regular_price: float = Field(default=0.0)
    sale_price: float | None = Field(default=None)
    on_sale: bool = Field(default=False)
    status: str = Field(default="publish", index=True)  # publish, draft, pending, private
    featured: bool = Field(default=False)
    catalog_visibility: str = Field(default="visible")  # visible, catalog, search, hidden
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
    virtual: bool = Field(default=False)
    downloadable: bool = Field(default=False)
    downloads: List[Dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    download_limit: int | None = Field(default=-1)
    download_expiry: int | None = Field(default=-1)
    sold_individually: bool = Field(default=False)
    external_url: str | None = Field(default=None)
    button_text: str | None = Field(default=None)
    menu_order: int = Field(default=0)
    purchasable: bool = Field(default=True)
    images: List[Dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))


class Product(ProductBase, table=True):  # type: ignore[call-arg]
    """Product model for database."""
    __tablename__ = "product"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    workspace_id: UUIDstr = Field(index=True, foreign_key="workspace.id")
    created_by: UUIDstr = Field(index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Essential relationships only (complex many-to-many disabled for now)
    workspace: "Workspace" = Relationship(back_populates="products")
    creator: "User" = Relationship(
        back_populates="created_products",
        sa_relationship_kwargs={"foreign_keys": "Product.created_by"}
    )

    # Many-to-many relationship with categories (temporarily disabled)
    # categories: List["ProductCategory"] = Relationship(
    #     back_populates="products",
    #     link_model=ProductCategoryLink
    # )

    # Many-to-many relationship with attributes (temporarily disabled)
    # attributes: List["ProductAttribute"] = Relationship(
    #     back_populates="products",
    #     link_model=ProductAttributeLink
    # )

    # One-to-many relationship with variations (temporarily disabled)
    # variations: List["ProductVariation"] = Relationship(
    #     back_populates="product",
    #     sa_relationship_kwargs={"cascade": "delete"}
    # )

    # One-to-many relationship with meta data (temporarily disabled)
    # meta_data: List["ProductMeta"] = Relationship(
    #     back_populates="product",
    #     sa_relationship_kwargs={"cascade": "delete"}
    # )

    # One-to-many relationship with reviews (temporarily disabled)
    # reviews: List["ProductReview"] = Relationship(
    #     back_populates="product",
    #     sa_relationship_kwargs={"cascade": "delete"}
    # )


class ProductCreate(ProductBase):
    """Schema for creating a product."""
    workspace_id: UUIDstr
    category_ids: List[UUIDstr] | None = None
    attribute_ids: List[UUIDstr] | None = None


class ProductRead(ProductBase):
    """Schema for reading a product."""
    id: UUIDstr
    workspace_id: UUIDstr
    created_by: UUIDstr
    created_at: datetime
    updated_at: datetime


class ProductUpdate(SQLModel):
    """Schema for updating a product."""
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    short_description: str | None = None
    sku: str | None = None
    price: float | None = None
    regular_price: float | None = None
    sale_price: float | None = None
    on_sale: bool | None = None
    status: str | None = None
    featured: bool | None = None
    catalog_visibility: str | None = None
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
    virtual: bool | None = None
    downloadable: bool | None = None
    downloads: List[Dict[str, Any]] | None = None
    download_limit: int | None = None
    download_expiry: int | None = None
    sold_individually: bool | None = None
    external_url: str | None = None
    button_text: str | None = None
    menu_order: int | None = None
    purchasable: bool | None = None
    images: List[Dict[str, Any]] | None = None
    category_ids: List[UUIDstr] | None = None
    attribute_ids: List[UUIDstr] | None = None
