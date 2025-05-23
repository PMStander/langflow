from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import Product
from langflow.services.database.models.crm.product_review import (
    ProductReview,
    ProductReviewCreate,
    ProductReviewRead,
    ProductReviewUpdate,
)
from langflow.api.v1.crm.utils import (
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.error_handling import handle_exceptions

router = APIRouter(prefix="/product-reviews", tags=["Product Reviews"])


@router.post("", response_model=ProductReviewRead, status_code=201)
@handle_exceptions
async def create_product_review(
    *,
    session: DbSession,
    review: ProductReviewCreate,
    current_user: CurrentActiveUser | None = None,
):
    """Create a new product review."""
    # Check if product exists
    product = (
        await session.exec(
            select(Product)
            .where(Product.id == review.product_id)
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    
    # Create review
    db_review = ProductReview.model_validate(review)
    
    # Set created_by if user is authenticated
    if current_user:
        db_review.created_by = current_user.id
    
    # Update timestamps
    update_entity_timestamps(db_review, is_new=True)
    session.add(db_review)
    await session.commit()
    await session.refresh(db_review)
    
    return db_review


@router.get("", response_model=PaginatedResponse[ProductReviewRead], status_code=200)
@handle_exceptions
async def read_product_reviews(
    *,
    session: DbSession,
    product_id: UUID | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all product reviews."""
    # Build query
    query = select(ProductReview)
    
    # Filter by product if provided
    if product_id:
        query = query.where(ProductReview.product_id == product_id)
    
    # Filter by status if provided
    if status:
        query = query.where(ProductReview.status == status)
    
    # Order by created_at (newest first)
    query = query.order_by(ProductReview.created_at.desc())
    
    # Paginate results
    reviews, metadata = await paginate_query(session, query, page, size)
    
    # Return paginated response
    return PaginatedResponse(items=reviews, metadata=metadata)


@router.get("/{review_id}", response_model=ProductReviewRead, status_code=200)
@handle_exceptions
async def read_product_review(
    *,
    session: DbSession,
    review_id: UUID,
):
    """Get a specific product review."""
    # Get the review
    review = (
        await session.exec(
            select(ProductReview)
            .where(ProductReview.id == review_id)
        )
    ).first()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product review not found",
        )
    
    return review


@router.patch("/{review_id}", response_model=ProductReviewRead, status_code=200)
@handle_exceptions
async def update_product_review(
    *,
    session: DbSession,
    review_id: UUID,
    review: ProductReviewUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product review (admin only)."""
    # Get the review
    db_review = (
        await session.exec(
            select(ProductReview)
            .where(ProductReview.id == review_id)
        )
    ).first()
    
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product review not found",
        )
    
    # Check if user has access to the product
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == db_review.product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this review",
        )
    
    # Update review fields and timestamps
    review_data = review.model_dump(exclude_unset=True)
    update_entity_timestamps(db_review, update_data=review_data)
    
    await session.commit()
    await session.refresh(db_review)
    
    return db_review


@router.delete("/{review_id}", status_code=204)
@handle_exceptions
async def delete_product_review(
    *,
    session: DbSession,
    review_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product review (admin only)."""
    # Get the review
    db_review = (
        await session.exec(
            select(ProductReview)
            .where(ProductReview.id == review_id)
        )
    ).first()
    
    if not db_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product review not found",
        )
    
    # Check if user has access to the product
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == db_review.product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this review",
        )
    
    await session.delete(db_review)
    await session.commit()
    
    return None
