from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import Product
from langflow.services.database.models.crm.product_variation import (
    ProductVariation,
    ProductVariationCreate,
    ProductVariationRead,
    ProductVariationUpdate,
)
from langflow.api.v1.crm.utils import (
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/product-variations", tags=["Product Variations"])


@router.post("", response_model=ProductVariationRead, status_code=201)
async def create_product_variation(
    *,
    session: DbSession,
    variation: ProductVariationCreate,
    current_user: CurrentActiveUser,
):
    """Create a new product variation."""
    try:
        # Check if product exists and user has access to it
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == variation.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )

        # Create product variation
        db_variation = ProductVariation.model_validate(variation)

        # Update timestamps
        update_entity_timestamps(db_variation, is_new=True)
        session.add(db_variation)
        await session.commit()
        await session.refresh(db_variation)

        # Invalidate dashboard cache since product variation data has changed
        invalidate_cache("get_workspace_stats")

        return db_variation
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create product variation: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("", response_model=PaginatedResponse[ProductVariationRead], status_code=200)
async def read_product_variations(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    product_id: UUID | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all product variations the user has access to."""
    try:
        # Build query for products the user has access to
        product_query = select(Product).where(get_entity_access_filter(Product, current_user.id))
        
        # Get the product IDs
        product_ids = [p.id for p in (await session.exec(product_query)).all()]
        
        if not product_ids:
            return PaginatedResponse(
                items=[],
                metadata={"page": page, "size": size, "total": 0, "pages": 0}
            )
        
        # Build query for variations
        query = select(ProductVariation).where(ProductVariation.product_id.in_(product_ids))
        
        # Filter by product if provided
        if product_id:
            if product_id not in product_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found or access denied",
                )
            query = query.where(ProductVariation.product_id == product_id)
        
        # Order by created_at
        query = query.order_by(ProductVariation.created_at.desc())
        
        # Paginate results
        variations, metadata = await paginate_query(session, query, page, size)
        
        # Return paginated response
        return PaginatedResponse(items=variations, metadata=metadata)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{variation_id}", response_model=ProductVariationRead, status_code=200)
async def read_product_variation(
    *,
    session: DbSession,
    variation_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific product variation."""
    try:
        # Get the variation
        variation = (
            await session.exec(
                select(ProductVariation)
                .where(ProductVariation.id == variation_id)
            )
        ).first()
        
        if not variation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variation not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == variation.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        return variation
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{variation_id}", response_model=ProductVariationRead, status_code=200)
async def update_product_variation(
    *,
    session: DbSession,
    variation_id: UUID,
    variation: ProductVariationUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product variation."""
    try:
        # Get the variation
        db_variation = (
            await session.exec(
                select(ProductVariation)
                .where(ProductVariation.id == variation_id)
            )
        ).first()
        
        if not db_variation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variation not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == db_variation.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        # Update variation fields and timestamps
        variation_data = variation.model_dump(exclude_unset=True)
        update_entity_timestamps(db_variation, update_data=variation_data)
        
        await session.commit()
        await session.refresh(db_variation)
        
        # Invalidate dashboard cache since product variation data has changed
        invalidate_cache("get_workspace_stats")
        
        return db_variation
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{variation_id}", status_code=204)
async def delete_product_variation(
    *,
    session: DbSession,
    variation_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product variation."""
    try:
        # Get the variation
        db_variation = (
            await session.exec(
                select(ProductVariation)
                .where(ProductVariation.id == variation_id)
            )
        ).first()
        
        if not db_variation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product variation not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == db_variation.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        await session.delete(db_variation)
        await session.commit()
        
        # Invalidate dashboard cache since product variation data has changed
        invalidate_cache("get_workspace_stats")
        
        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
