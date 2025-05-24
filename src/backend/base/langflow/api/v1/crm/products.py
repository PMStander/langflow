from uuid import UUID

from fastapi import APIRouter, HTTPException
from .error_handling import get_http_status_code, handle_exceptions
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product import (
    Product,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductRead, status_code=201)
@handle_exceptions
async def create_product(
    *,
    session: DbSession,
    product: ProductCreate,
    current_user: CurrentActiveUser,
):
    """Create a new product."""
    # Check if user has access to the workspace
    await check_workspace_access(session, product.workspace_id, current_user)

    # Create product
    db_product = Product.model_validate(product)
    db_product.created_by = current_user.id

    # Update timestamps
    update_entity_timestamps(db_product, is_new=True)
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    # Handle category associations if provided
    if product.category_ids:
        for category_id in product.category_ids:
            link = {"product_id": db_product.id, "category_id": category_id}
            await session.execute(
                "INSERT INTO product_category_link (product_id, category_id) VALUES (:product_id, :category_id)",
                link
            )
        await session.commit()

    # Handle attribute associations if provided
    if product.attribute_ids:
        for attribute_id in product.attribute_ids:
            link = {"product_id": db_product.id, "attribute_id": attribute_id}
            await session.execute(
                "INSERT INTO product_attribute_link (product_id, attribute_id) VALUES (:product_id, :attribute_id)",
                link
            )
        await session.commit()

    # Invalidate dashboard cache since product data has changed
    invalidate_cache("get_workspace_stats")

    return db_product


@router.get("", response_model=PaginatedResponse[ProductRead], status_code=200)
@handle_exceptions
async def read_products(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    product_status: str | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all products the user has access to."""
    # Build query
    query = select(Product).where(get_entity_access_filter(Product, current_user.id))

    # Filter by workspace if provided
    if workspace_id:
        query = query.where(Product.workspace_id == workspace_id)

    # Filter by status if provided
    if product_status:
        query = query.where(Product.status == product_status)

    # Order by created_at (newest first)
    query = query.order_by(Product.created_at.desc())

    # Paginate results
    products, metadata = await paginate_query(session, query, page, size)

    # Return paginated response
    return PaginatedResponse(items=products, metadata=metadata)


@router.get("/{product_id}", response_model=ProductRead, status_code=200)
@handle_exceptions
async def read_product(
    *,
    session: DbSession,
    product_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific product."""
    # Check if product exists and user has access to it
    product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()

    if not product:
        raise HTTPException(
            status_code=get_http_status_code("HTTP_404_NOT_FOUND"),
            detail="Product not found or access denied",
        )

    return product


@router.patch("/{product_id}", response_model=ProductRead, status_code=200)
@handle_exceptions
async def update_product(
    *,
    session: DbSession,
    product_id: UUID,
    product: ProductUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product."""
    # Check if product exists and user has access to it
    db_product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=get_http_status_code("HTTP_404_NOT_FOUND"),
            detail="Product not found or access denied",
        )

    # Update product fields and timestamps
    product_data = product.model_dump(exclude_unset=True)
    update_entity_timestamps(db_product, update_data=product_data)

    # Handle category associations if provided
    if product.category_ids is not None:
        # Remove existing associations
        await session.execute(
            "DELETE FROM product_category_link WHERE product_id = :product_id",
            {"product_id": product_id}
        )

        # Add new associations
        for category_id in product.category_ids:
            link = {"product_id": product_id, "category_id": category_id}
            await session.execute(
                "INSERT INTO product_category_link (product_id, category_id) VALUES (:product_id, :category_id)",
                link
            )

    # Handle attribute associations if provided
    if product.attribute_ids is not None:
        # Remove existing associations
        await session.execute(
            "DELETE FROM product_attribute_link WHERE product_id = :product_id",
            {"product_id": product_id}
        )

        # Add new associations
        for attribute_id in product.attribute_ids:
            link = {"product_id": product_id, "attribute_id": attribute_id}
            await session.execute(
                "INSERT INTO product_attribute_link (product_id, attribute_id) VALUES (:product_id, :attribute_id)",
                link
            )

    await session.commit()
    await session.refresh(db_product)

    # Invalidate dashboard cache since product data has changed
    invalidate_cache("get_workspace_stats")

    return db_product


@router.delete("/{product_id}", status_code=204)
@handle_exceptions
async def delete_product(
    *,
    session: DbSession,
    product_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product."""
    # Check if product exists and user has access to it
    db_product = (
        await session.exec(
            select(Product)
            .where(
                Product.id == product_id,
                get_entity_access_filter(Product, current_user.id)
            )
        )
    ).first()

    if not db_product:
        raise HTTPException(
            status_code=get_http_status_code("HTTP_404_NOT_FOUND"),
            detail="Product not found or access denied",
        )

    await session.delete(db_product)
    await session.commit()

    # Invalidate dashboard cache since product data has changed
    invalidate_cache("get_workspace_stats")

    return None
