from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product_category import (
    ProductCategory,
    ProductCategoryCreate,
    ProductCategoryRead,
    ProductCategoryUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/product-categories", tags=["Product Categories"])


@router.post("", response_model=ProductCategoryRead, status_code=201)
async def create_product_category(
    *,
    session: DbSession,
    product_category: ProductCategoryCreate,
    current_user: CurrentActiveUser,
):
    """Create a new product category."""
    try:
        # Check if user has access to the workspace
        await check_workspace_access(session, product_category.workspace_id, current_user)

        # Create product category
        db_product_category = ProductCategory.model_validate(product_category)
        db_product_category.created_by = current_user.id

        # Update timestamps
        update_entity_timestamps(db_product_category, is_new=True)
        session.add(db_product_category)
        await session.commit()
        await session.refresh(db_product_category)

        # Invalidate dashboard cache since product category data has changed
        invalidate_cache("get_workspace_stats")

        return db_product_category
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create product category: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("", response_model=PaginatedResponse[ProductCategoryRead], status_code=200)
async def read_product_categories(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    parent_id: UUID | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all product categories the user has access to."""
    try:
        # Build query
        query = select(ProductCategory).where(get_entity_access_filter(ProductCategory, current_user.id))

        # Filter by workspace if provided
        if workspace_id:
            query = query.where(ProductCategory.workspace_id == workspace_id)

        # Filter by parent category if provided
        if parent_id:
            query = query.where(ProductCategory.parent_id == parent_id)

        # Order by name
        query = query.order_by(ProductCategory.name)

        # Paginate results
        categories, metadata = await paginate_query(session, query, page, size)

        # Return paginated response
        return PaginatedResponse(items=categories, metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{category_id}", response_model=ProductCategoryRead, status_code=200)
async def read_product_category(
    *,
    session: DbSession,
    category_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific product category."""
    try:
        # Check if category exists and user has access to it
        category = (
            await session.exec(
                select(ProductCategory)
                .where(
                    ProductCategory.id == category_id,
                    get_entity_access_filter(ProductCategory, current_user.id)
                )
            )
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product category not found or access denied",
            )

        return category
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{category_id}", response_model=ProductCategoryRead, status_code=200)
async def update_product_category(
    *,
    session: DbSession,
    category_id: UUID,
    product_category: ProductCategoryUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product category."""
    try:
        # Check if category exists and user has access to it
        db_category = (
            await session.exec(
                select(ProductCategory)
                .where(
                    ProductCategory.id == category_id,
                    get_entity_access_filter(ProductCategory, current_user.id)
                )
            )
        ).first()

        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product category not found or access denied",
            )

        # Update category fields and timestamps
        category_data = product_category.model_dump(exclude_unset=True)
        update_entity_timestamps(db_category, update_data=category_data)

        await session.commit()
        await session.refresh(db_category)

        # Invalidate dashboard cache since product category data has changed
        invalidate_cache("get_workspace_stats")

        return db_category
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{category_id}", status_code=204)
async def delete_product_category(
    *,
    session: DbSession,
    category_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product category."""
    try:
        # Check if category exists and user has access to it
        db_category = (
            await session.exec(
                select(ProductCategory)
                .where(
                    ProductCategory.id == category_id,
                    get_entity_access_filter(ProductCategory, current_user.id)
                )
            )
        ).first()

        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product category not found or access denied",
            )

        await session.delete(db_category)
        await session.commit()

        # Invalidate dashboard cache since product category data has changed
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
