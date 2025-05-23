from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.book import (
    BookTemplate,
    BookTemplateCreate,
    BookTemplateRead,
    BookTemplateUpdate,
)

router = APIRouter(tags=["Book Templates"], prefix="/book-templates")


@router.post("/", response_model=BookTemplateRead, status_code=201)
async def create_book_template(
    template: BookTemplateCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookTemplate:
    """Create a new book template."""
    new_template = BookTemplate.model_validate(template, from_attributes=True)
    new_template.user_id = current_user.id
    
    try:
        session.add(new_template)
        await session.commit()
        await session.refresh(new_template)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating book template: {e}") from e
    
    return new_template


@router.get("/", response_model=List[BookTemplateRead])
async def get_book_templates(
    session: DbSession,
    current_user: CurrentActiveUser,
    category: Optional[str] = Query(None, description="Filter by category"),
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    include_system: bool = Query(True, description="Include system templates"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[BookTemplate]:
    """Get all book templates."""
    # Get system templates and user's templates
    query = select(BookTemplate).where(
        (BookTemplate.is_system == True) | (BookTemplate.user_id == current_user.id)  # noqa: E712
    )
    
    if not include_system:
        query = select(BookTemplate).where(BookTemplate.user_id == current_user.id)
    
    if category:
        query = query.where(BookTemplate.category == category)
    
    if template_type:
        query = query.where(BookTemplate.template_type == template_type)
    
    query = query.offset(skip).limit(limit)
    templates = (await session.exec(query)).all()
    return list(templates)


@router.get("/{template_id}", response_model=BookTemplateRead)
async def get_book_template(
    template_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookTemplate:
    """Get a book template by ID."""
    template = (
        await session.exec(
            select(BookTemplate).where(
                BookTemplate.id == template_id,
                (BookTemplate.is_system == True) | (BookTemplate.user_id == current_user.id),  # noqa: E712
            )
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Book template not found")
    
    return template


@router.patch("/{template_id}", response_model=BookTemplateRead)
async def update_book_template(
    template_id: UUID,
    template_update: BookTemplateUpdate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookTemplate:
    """Update a book template."""
    template = (
        await session.exec(
            select(BookTemplate).where(BookTemplate.id == template_id, BookTemplate.user_id == current_user.id)
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Book template not found or you don't have permission to update it")
    
    # System templates cannot be updated by users
    if template.is_system:
        raise HTTPException(status_code=403, detail="System templates cannot be updated")
    
    template_data = template_update.model_dump(exclude_unset=True)
    for key, value in template_data.items():
        setattr(template, key, value)
    
    try:
        session.add(template)
        await session.commit()
        await session.refresh(template)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating book template: {e}") from e
    
    return template


@router.delete("/{template_id}", status_code=204)
async def delete_book_template(
    template_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> None:
    """Delete a book template."""
    template = (
        await session.exec(
            select(BookTemplate).where(BookTemplate.id == template_id, BookTemplate.user_id == current_user.id)
        )
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Book template not found or you don't have permission to delete it")
    
    # System templates cannot be deleted by users
    if template.is_system:
        raise HTTPException(status_code=403, detail="System templates cannot be deleted")
    
    try:
        await session.delete(template)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting book template: {e}") from e
