from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.crm.product_attribute import (
    ProductAttribute,
    ProductAttributeCreate,
    ProductAttributeRead,
    ProductAttributeUpdate,
    ProductAttributeTerm,
    ProductAttributeTermCreate,
    ProductAttributeTermRead,
    ProductAttributeTermUpdate,
)
from langflow.api.v1.crm.utils import (
    check_workspace_access,
    get_entity_access_filter,
    update_entity_timestamps,
    paginate_query,
)
from langflow.api.v1.crm.models import PaginatedResponse
from langflow.api.v1.crm.cache import invalidate_cache

router = APIRouter(prefix="/product-attributes", tags=["Product Attributes"])


@router.post("", response_model=ProductAttributeRead, status_code=201)
async def create_product_attribute(
    *,
    session: DbSession,
    product_attribute: ProductAttributeCreate,
    current_user: CurrentActiveUser,
):
    """Create a new product attribute."""
    try:
        # Check if user has access to the workspace
        await check_workspace_access(session, product_attribute.workspace_id, current_user)

        # Create product attribute
        db_product_attribute = ProductAttribute.model_validate(product_attribute)
        db_product_attribute.created_by = current_user.id

        # Update timestamps
        update_entity_timestamps(db_product_attribute, is_new=True)
        session.add(db_product_attribute)
        await session.commit()
        await session.refresh(db_product_attribute)

        # Invalidate dashboard cache since product attribute data has changed
        invalidate_cache("get_workspace_stats")

        return db_product_attribute
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create product attribute: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("", response_model=PaginatedResponse[ProductAttributeRead], status_code=200)
async def read_product_attributes(
    *,
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: UUID | None = None,
    page: int = 1,
    size: int = 10,
):
    """Get all product attributes the user has access to."""
    try:
        # Build query
        query = select(ProductAttribute).where(get_entity_access_filter(ProductAttribute, current_user.id))

        # Filter by workspace if provided
        if workspace_id:
            query = query.where(ProductAttribute.workspace_id == workspace_id)

        # Order by name
        query = query.order_by(ProductAttribute.name)

        # Paginate results
        attributes, metadata = await paginate_query(session, query, page, size)

        # Return paginated response
        return PaginatedResponse(items=attributes, metadata=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{attribute_id}", response_model=ProductAttributeRead, status_code=200)
async def read_product_attribute(
    *,
    session: DbSession,
    attribute_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific product attribute."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        return attribute
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{attribute_id}", response_model=ProductAttributeRead, status_code=200)
async def update_product_attribute(
    *,
    session: DbSession,
    attribute_id: UUID,
    product_attribute: ProductAttributeUpdate,
    current_user: CurrentActiveUser,
):
    """Update a product attribute."""
    try:
        # Check if attribute exists and user has access to it
        db_attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not db_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Update attribute fields and timestamps
        attribute_data = product_attribute.model_dump(exclude_unset=True)
        update_entity_timestamps(db_attribute, update_data=attribute_data)

        await session.commit()
        await session.refresh(db_attribute)

        # Invalidate dashboard cache since product attribute data has changed
        invalidate_cache("get_workspace_stats")

        return db_attribute
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{attribute_id}", status_code=204)
async def delete_product_attribute(
    *,
    session: DbSession,
    attribute_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete a product attribute."""
    try:
        # Check if attribute exists and user has access to it
        db_attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not db_attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        await session.delete(db_attribute)
        await session.commit()

        # Invalidate dashboard cache since product attribute data has changed
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


# Attribute Terms Endpoints

@router.post("/{attribute_id}/terms", response_model=ProductAttributeTermRead, status_code=201)
async def create_attribute_term(
    *,
    session: DbSession,
    attribute_id: UUID,
    term: ProductAttributeTermCreate,
    current_user: CurrentActiveUser,
):
    """Create a new attribute term."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Create attribute term
        db_term = ProductAttributeTerm.model_validate(term)
        db_term.attribute_id = attribute_id

        # Update timestamps
        update_entity_timestamps(db_term, is_new=True)
        session.add(db_term)
        await session.commit()
        await session.refresh(db_term)

        return db_term
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not create attribute term: {str(e)}",
        ) from e
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{attribute_id}/terms", response_model=PaginatedResponse[ProductAttributeTermRead], status_code=200)
async def read_attribute_terms(
    *,
    session: DbSession,
    attribute_id: UUID,
    current_user: CurrentActiveUser,
    page: int = 1,
    size: int = 10,
):
    """Get all terms for a specific attribute."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Build query for terms
        query = select(ProductAttributeTerm).where(ProductAttributeTerm.attribute_id == attribute_id)

        # Order by menu_order and name
        query = query.order_by(ProductAttributeTerm.menu_order, ProductAttributeTerm.name)

        # Paginate results
        terms, metadata = await paginate_query(session, query, page, size)

        # Return paginated response
        return PaginatedResponse(items=terms, metadata=metadata)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.get("/{attribute_id}/terms/{term_id}", response_model=ProductAttributeTermRead, status_code=200)
async def read_attribute_term(
    *,
    session: DbSession,
    attribute_id: UUID,
    term_id: UUID,
    current_user: CurrentActiveUser,
):
    """Get a specific attribute term."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Get the term
        term = (
            await session.exec(
                select(ProductAttributeTerm)
                .where(
                    ProductAttributeTerm.id == term_id,
                    ProductAttributeTerm.attribute_id == attribute_id
                )
            )
        ).first()

        if not term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute term not found",
            )

        return term
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.patch("/{attribute_id}/terms/{term_id}", response_model=ProductAttributeTermRead, status_code=200)
async def update_attribute_term(
    *,
    session: DbSession,
    attribute_id: UUID,
    term_id: UUID,
    term: ProductAttributeTermUpdate,
    current_user: CurrentActiveUser,
):
    """Update an attribute term."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Get the term
        db_term = (
            await session.exec(
                select(ProductAttributeTerm)
                .where(
                    ProductAttributeTerm.id == term_id,
                    ProductAttributeTerm.attribute_id == attribute_id
                )
            )
        ).first()

        if not db_term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute term not found",
            )

        # Update term fields and timestamps
        term_data = term.model_dump(exclude_unset=True)
        update_entity_timestamps(db_term, update_data=term_data)

        await session.commit()
        await session.refresh(db_term)

        return db_term
    except Exception as e:
        await session.rollback()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e


@router.delete("/{attribute_id}/terms/{term_id}", status_code=204)
async def delete_attribute_term(
    *,
    session: DbSession,
    attribute_id: UUID,
    term_id: UUID,
    current_user: CurrentActiveUser,
):
    """Delete an attribute term."""
    try:
        # Check if attribute exists and user has access to it
        attribute = (
            await session.exec(
                select(ProductAttribute)
                .where(
                    ProductAttribute.id == attribute_id,
                    get_entity_access_filter(ProductAttribute, current_user.id)
                )
            )
        ).first()

        if not attribute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product attribute not found or access denied",
            )

        # Get the term
        db_term = (
            await session.exec(
                select(ProductAttributeTerm)
                .where(
                    ProductAttributeTerm.id == term_id,
                    ProductAttributeTerm.attribute_id == attribute_id
                )
            )
        ).first()

        if not db_term:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attribute term not found",
            )

        await session.delete(db_term)
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
