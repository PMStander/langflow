from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import Product
from langflow.services.database.models.crm.product_meta import (
    ProductMeta,
    ProductMetaCreate,
    ProductMetaRead,
    ProductMetaUpdate,
)
from langflow.api.v1.crm.utils import (
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/product-meta", tags=["Product Meta"])


@router.post("", response_model=ProductMetaRead, status_code=201)
async def create_product_meta(
    *,
    session: DbSession,
    meta: ProductMetaCreate,
    current_user: CurrentActiveUser,
):
    """Create a new product meta."""
    try:
        # Check if product exists and user has access to it
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == meta.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )

        # Create product meta
        db_meta = ProductMeta.model_validate(meta)

        # Update timestamps
        update_entity_timestamps(db_meta, is_new=True)
        session.add(db_meta)
        await session.commit()
        await session.refresh(db_meta)

        return db_meta
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create product meta: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("", response_model=PaginatedResponse[ProductMetaRead], status_code=200)
async def read_product_meta(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    product_id: UUID | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all product meta the user has access to."""
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
        
        # Build query for meta
        query = select(ProductMeta).where(ProductMeta.product_id.in_(product_ids))
        
        # Filter by product if provided
        if product_id:
            if product_id not in product_ids:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found or access denied",
                )
            query = query.where(ProductMeta.product_id == product_id)
        
        # Order by key
        query = query.order_by(ProductMeta.key)
        
        # Paginate results
        meta_items, metadata = await paginate_query(session, query, page, size)
        
        # Return paginated response
        return PaginatedResponse(items=meta_items, metadata=metadata)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{meta_id}", response_model=ProductMetaRead, status_code=200)
async def read_product_meta_item(
    *,
    session: DbSession,
    meta_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific product meta item."""
    try:
        # Get the meta item
        meta_item = (
            await session.exec(
                select(ProductMeta)
                .where(ProductMeta.id == meta_id)
            )
        ).first()
        
        if not meta_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product meta not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == meta_item.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        return meta_item
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{meta_id}", response_model=ProductMetaRead, status_code=200)
async def update_product_meta(
    *,
    session: DbSession,
    meta_id: UUID,
    meta: ProductMetaUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product meta item."""
    try:
        # Get the meta item
        db_meta = (
            await session.exec(
                select(ProductMeta)
                .where(ProductMeta.id == meta_id)
            )
        ).first()
        
        if not db_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product meta not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == db_meta.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        # Update meta fields and timestamps
        meta_data = meta.model_dump(exclude_unset=True)
        update_entity_timestamps(db_meta, update_data=meta_data)
        
        await session.commit()
        await session.refresh(db_meta)
        
        return db_meta
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{meta_id}", status_code=204)
async def delete_product_meta(
    *,
    session: DbSession,
    meta_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product meta item."""
    try:
        # Get the meta item
        db_meta = (
            await session.exec(
                select(ProductMeta)
                .where(ProductMeta.id == meta_id)
            )
        ).first()
        
        if not db_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product meta not found",
            )
        
        # Check if user has access to the product
        product = (
            await session.exec(
                select(Product)
                .where(
                    Product.id == db_meta.product_id,
                    get_entity_access_filter(Product, current_user.id)
                )
            )
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found or access denied",
            )
        
        await session.delete(db_meta)
        await session.commit()
        
        return None
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
