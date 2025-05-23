from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.database.models.book import (
    Book,
    BookCover,
    BookCoverCreate,
    BookCoverRead,
    BookCoverUpdate,
    BookCreate,
    BookInterior,
    BookInteriorCreate,
    BookInteriorRead,
    BookInteriorUpdate,
    BookPage,
    BookPageCreate,
    BookPageRead,
    BookPageUpdate,
    BookRead,
    BookUpdate,
)

router = APIRouter(tags=["Books"], prefix="/books")


@router.post("/", response_model=BookRead, status_code=201)
async def create_book(
    book: BookCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> Book:
    """Create a new book."""
    new_book = Book.model_validate(book, from_attributes=True)
    new_book.user_id = current_user.id
    try:
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating book: {e}") from e

    return new_book


@router.get("/", response_model=List[BookRead])
async def get_books(
    session: DbSession,
    current_user: CurrentActiveUser,
    workspace_id: Optional[UUID] = Query(None, description="Filter by workspace ID"),
    book_type: Optional[str] = Query(None, description="Filter by book type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[Book]:
    """Get all books for the current user."""
    query = select(Book).where(Book.user_id == current_user.id)
    
    if workspace_id:
        query = query.where(Book.workspace_id == workspace_id)
    
    if book_type:
        query = query.where(Book.book_type == book_type)
    
    query = query.offset(skip).limit(limit)
    books = (await session.exec(query)).all()
    return list(books)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> Book:
    """Get a book by ID."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.patch("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: UUID,
    book_update: BookUpdate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> Book:
    """Update a book."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book_data = book_update.model_dump(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)
    
    try:
        session.add(book)
        await session.commit()
        await session.refresh(book)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating book: {e}") from e
    
    return book


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> None:
    """Delete a book."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        await session.delete(book)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting book: {e}") from e


# Book Cover endpoints
@router.post("/{book_id}/cover", response_model=BookCoverRead, status_code=201)
async def create_book_cover(
    book_id: UUID,
    cover: BookCoverCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookCover:
    """Create a book cover."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if cover already exists
    existing_cover = (await session.exec(select(BookCover).where(BookCover.book_id == book_id))).first()
    if existing_cover:
        raise HTTPException(status_code=400, detail="Book cover already exists")
    
    new_cover = BookCover.model_validate(cover, from_attributes=True)
    new_cover.book_id = book_id
    
    try:
        session.add(new_cover)
        await session.commit()
        await session.refresh(new_cover)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating book cover: {e}") from e
    
    return new_cover


@router.get("/{book_id}/cover", response_model=BookCoverRead)
async def get_book_cover(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookCover:
    """Get a book cover."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    cover = (await session.exec(select(BookCover).where(BookCover.book_id == book_id))).first()
    if not cover:
        raise HTTPException(status_code=404, detail="Book cover not found")
    
    return cover


@router.patch("/{book_id}/cover", response_model=BookCoverRead)
async def update_book_cover(
    book_id: UUID,
    cover_update: BookCoverUpdate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookCover:
    """Update a book cover."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    cover = (await session.exec(select(BookCover).where(BookCover.book_id == book_id))).first()
    if not cover:
        raise HTTPException(status_code=404, detail="Book cover not found")
    
    cover_data = cover_update.model_dump(exclude_unset=True)
    for key, value in cover_data.items():
        setattr(cover, key, value)
    
    try:
        session.add(cover)
        await session.commit()
        await session.refresh(cover)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating book cover: {e}") from e
    
    return cover


# Book Interior endpoints
@router.post("/{book_id}/interior", response_model=BookInteriorRead, status_code=201)
async def create_book_interior(
    book_id: UUID,
    interior: BookInteriorCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookInterior:
    """Create a book interior."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if interior already exists
    existing_interior = (await session.exec(select(BookInterior).where(BookInterior.book_id == book_id))).first()
    if existing_interior:
        raise HTTPException(status_code=400, detail="Book interior already exists")
    
    new_interior = BookInterior.model_validate(interior, from_attributes=True)
    new_interior.book_id = book_id
    
    try:
        session.add(new_interior)
        await session.commit()
        await session.refresh(new_interior)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating book interior: {e}") from e
    
    return new_interior


@router.get("/{book_id}/interior", response_model=BookInteriorRead)
async def get_book_interior(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookInterior:
    """Get a book interior."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    interior = (await session.exec(select(BookInterior).where(BookInterior.book_id == book_id))).first()
    if not interior:
        raise HTTPException(status_code=404, detail="Book interior not found")
    
    return interior


@router.patch("/{book_id}/interior", response_model=BookInteriorRead)
async def update_book_interior(
    book_id: UUID,
    interior_update: BookInteriorUpdate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookInterior:
    """Update a book interior."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    interior = (await session.exec(select(BookInterior).where(BookInterior.book_id == book_id))).first()
    if not interior:
        raise HTTPException(status_code=404, detail="Book interior not found")
    
    interior_data = interior_update.model_dump(exclude_unset=True)
    for key, value in interior_data.items():
        setattr(interior, key, value)
    
    try:
        session.add(interior)
        await session.commit()
        await session.refresh(interior)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating book interior: {e}") from e
    
    return interior


# Book Page endpoints
@router.post("/{book_id}/pages", response_model=BookPageRead, status_code=201)
async def create_book_page(
    book_id: UUID,
    page: BookPageCreate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookPage:
    """Create a book page."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Check if page number already exists
    existing_page = (
        await session.exec(
            select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page.page_number)
        )
    ).first()
    if existing_page:
        raise HTTPException(status_code=400, detail=f"Page number {page.page_number} already exists")
    
    new_page = BookPage.model_validate(page, from_attributes=True)
    new_page.book_id = book_id
    
    try:
        session.add(new_page)
        await session.commit()
        await session.refresh(new_page)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating book page: {e}") from e
    
    return new_page


@router.get("/{book_id}/pages", response_model=List[BookPageRead])
async def get_book_pages(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> List[BookPage]:
    """Get all pages for a book."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    query = select(BookPage).where(BookPage.book_id == book_id).order_by(BookPage.page_number).offset(skip).limit(limit)
    pages = (await session.exec(query)).all()
    return list(pages)


@router.get("/{book_id}/pages/{page_number}", response_model=BookPageRead)
async def get_book_page(
    book_id: UUID,
    page_number: int,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookPage:
    """Get a book page by page number."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    page = (
        await session.exec(
            select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page_number)
        )
    ).first()
    if not page:
        raise HTTPException(status_code=404, detail=f"Page number {page_number} not found")
    
    return page


@router.patch("/{book_id}/pages/{page_number}", response_model=BookPageRead)
async def update_book_page(
    book_id: UUID,
    page_number: int,
    page_update: BookPageUpdate,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> BookPage:
    """Update a book page."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    page = (
        await session.exec(
            select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page_number)
        )
    ).first()
    if not page:
        raise HTTPException(status_code=404, detail=f"Page number {page_number} not found")
    
    page_data = page_update.model_dump(exclude_unset=True)
    
    # If page number is being updated, check if the new page number already exists
    if "page_number" in page_data and page_data["page_number"] != page_number:
        existing_page = (
            await session.exec(
                select(BookPage).where(
                    BookPage.book_id == book_id, BookPage.page_number == page_data["page_number"]
                )
            )
        ).first()
        if existing_page:
            raise HTTPException(
                status_code=400, detail=f"Page number {page_data['page_number']} already exists"
            )
    
    for key, value in page_data.items():
        setattr(page, key, value)
    
    try:
        session.add(page)
        await session.commit()
        await session.refresh(page)
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating book page: {e}") from e
    
    return page


@router.delete("/{book_id}/pages/{page_number}", status_code=204)
async def delete_book_page(
    book_id: UUID,
    page_number: int,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> None:
    """Delete a book page."""
    book = (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == current_user.id))).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    page = (
        await session.exec(
            select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page_number)
        )
    ).first()
    if not page:
        raise HTTPException(status_code=404, detail=f"Page number {page_number} not found")
    
    try:
        await session.delete(page)
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error deleting book page: {e}") from e
