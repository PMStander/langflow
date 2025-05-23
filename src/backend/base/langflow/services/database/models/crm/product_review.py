from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import Text, Column
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, Relationship, SQLModel

from langflow.schema.serialize import UUIDstr

if TYPE_CHECKING:
    from langflow.services.database.models.user import User
    from langflow.services.database.models.crm.product import Product


class ProductReviewBase(SQLModel):
    """Base model for ProductReview."""
    rating: int = Field(ge=1, le=5)  # Rating from 1 to 5
    title: str | None = Field(default=None)
    content: str | None = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="pending")  # pending, approved, rejected
    reviewer_name: str | None = Field(default=None)
    reviewer_email: str | None = Field(default=None)
    verified_purchase: bool = Field(default=False)


class ProductReview(ProductReviewBase, table=True):  # type: ignore[call-arg]
    """ProductReview model for database."""
    __tablename__ = "product_review"

    id: UUIDstr = Field(
        default_factory=uuid4,
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True, unique=True)
    )
    product_id: UUIDstr = Field(index=True, foreign_key="product.id")
    created_by: UUIDstr | None = Field(default=None, index=True, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Relationships
    product: "Product" = Relationship(back_populates="reviews")
    creator: Optional["User"] = Relationship(
        back_populates="created_product_reviews", 
        sa_relationship_kwargs={"foreign_keys": "ProductReview.created_by"}
    )


class ProductReviewCreate(ProductReviewBase):
    """Schema for creating a product review."""
    product_id: UUIDstr


class ProductReviewRead(ProductReviewBase):
    """Schema for reading a product review."""
    id: UUIDstr
    product_id: UUIDstr
    created_by: UUIDstr | None
    created_at: datetime
    updated_at: datetime


class ProductReviewUpdate(SQLModel):
    """Schema for updating a product review."""
    rating: int | None = None
    title: str | None = None
    content: str | None = None
    status: str | None = None
    reviewer_name: str | None = None
    reviewer_email: str | None = None
    verified_purchase: bool | None = None
