from typing import Dict, List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.base import Service
from langflow.services.database.models.book import (
    Book,
    BookCover,
    BookInterior,
    BookPage,
    BookTemplate,
)
from langflow.services.deps import get_db_service, get_session


class BookService(Service):
    """Service for managing books."""

    name = "book_service"

    async def get_book_by_id(self, book_id: UUID, user_id: UUID) -> Optional[Book]:
        """Get a book by ID."""
        async with get_session() as session:
            return await self._get_book_by_id(session, book_id, user_id)

    async def _get_book_by_id(self, session: AsyncSession, book_id: UUID, user_id: UUID) -> Optional[Book]:
        """Get a book by ID (internal method)."""
        return (await session.exec(select(Book).where(Book.id == book_id, Book.user_id == user_id))).first()

    async def get_books_by_user(
        self, user_id: UUID, workspace_id: Optional[UUID] = None, book_type: Optional[str] = None
    ) -> List[Book]:
        """Get all books for a user."""
        async with get_session() as session:
            query = select(Book).where(Book.user_id == user_id)
            
            if workspace_id:
                query = query.where(Book.workspace_id == workspace_id)
            
            if book_type:
                query = query.where(Book.book_type == book_type)
            
            return list((await session.exec(query)).all())

    async def create_book(self, book: Book) -> Book:
        """Create a new book."""
        async with get_session() as session:
            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book

    async def update_book(self, book: Book) -> Book:
        """Update a book."""
        async with get_session() as session:
            session.add(book)
            await session.commit()
            await session.refresh(book)
            return book

    async def delete_book(self, book_id: UUID, user_id: UUID) -> bool:
        """Delete a book."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return False
            
            await session.delete(book)
            await session.commit()
            return True

    # Book Cover methods
    async def get_book_cover(self, book_id: UUID, user_id: UUID) -> Optional[BookCover]:
        """Get a book cover."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return None
            
            return (await session.exec(select(BookCover).where(BookCover.book_id == book_id))).first()

    async def create_book_cover(self, cover: BookCover) -> BookCover:
        """Create a book cover."""
        async with get_session() as session:
            session.add(cover)
            await session.commit()
            await session.refresh(cover)
            return cover

    async def update_book_cover(self, cover: BookCover) -> BookCover:
        """Update a book cover."""
        async with get_session() as session:
            session.add(cover)
            await session.commit()
            await session.refresh(cover)
            return cover

    # Book Interior methods
    async def get_book_interior(self, book_id: UUID, user_id: UUID) -> Optional[BookInterior]:
        """Get a book interior."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return None
            
            return (await session.exec(select(BookInterior).where(BookInterior.book_id == book_id))).first()

    async def create_book_interior(self, interior: BookInterior) -> BookInterior:
        """Create a book interior."""
        async with get_session() as session:
            session.add(interior)
            await session.commit()
            await session.refresh(interior)
            return interior

    async def update_book_interior(self, interior: BookInterior) -> BookInterior:
        """Update a book interior."""
        async with get_session() as session:
            session.add(interior)
            await session.commit()
            await session.refresh(interior)
            return interior

    # Book Page methods
    async def get_book_pages(self, book_id: UUID, user_id: UUID) -> List[BookPage]:
        """Get all pages for a book."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return []
            
            query = select(BookPage).where(BookPage.book_id == book_id).order_by(BookPage.page_number)
            return list((await session.exec(query)).all())

    async def get_book_page(self, book_id: UUID, page_number: int, user_id: UUID) -> Optional[BookPage]:
        """Get a book page by page number."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return None
            
            return (
                await session.exec(
                    select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page_number)
                )
            ).first()

    async def create_book_page(self, page: BookPage) -> BookPage:
        """Create a book page."""
        async with get_session() as session:
            session.add(page)
            await session.commit()
            await session.refresh(page)
            return page

    async def update_book_page(self, page: BookPage) -> BookPage:
        """Update a book page."""
        async with get_session() as session:
            session.add(page)
            await session.commit()
            await session.refresh(page)
            return page

    async def delete_book_page(self, book_id: UUID, page_number: int, user_id: UUID) -> bool:
        """Delete a book page."""
        async with get_session() as session:
            book = await self._get_book_by_id(session, book_id, user_id)
            if not book:
                return False
            
            page = (
                await session.exec(
                    select(BookPage).where(BookPage.book_id == book_id, BookPage.page_number == page_number)
                )
            ).first()
            
            if not page:
                return False
            
            await session.delete(page)
            await session.commit()
            return True

    # Book Template methods
    async def get_book_templates(
        self, user_id: UUID, category: Optional[str] = None, template_type: Optional[str] = None, include_system: bool = True
    ) -> List[BookTemplate]:
        """Get all book templates."""
        async with get_session() as session:
            # Get system templates and user's templates
            query = select(BookTemplate).where(
                (BookTemplate.is_system == True) | (BookTemplate.user_id == user_id)  # noqa: E712
            )
            
            if not include_system:
                query = select(BookTemplate).where(BookTemplate.user_id == user_id)
            
            if category:
                query = query.where(BookTemplate.category == category)
            
            if template_type:
                query = query.where(BookTemplate.template_type == template_type)
            
            return list((await session.exec(query)).all())

    async def get_book_template(self, template_id: UUID, user_id: UUID) -> Optional[BookTemplate]:
        """Get a book template by ID."""
        async with get_session() as session:
            return (
                await session.exec(
                    select(BookTemplate).where(
                        BookTemplate.id == template_id,
                        (BookTemplate.is_system == True) | (BookTemplate.user_id == user_id),  # noqa: E712
                    )
                )
            ).first()

    async def create_book_template(self, template: BookTemplate) -> BookTemplate:
        """Create a book template."""
        async with get_session() as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template

    async def update_book_template(self, template: BookTemplate) -> BookTemplate:
        """Update a book template."""
        async with get_session() as session:
            session.add(template)
            await session.commit()
            await session.refresh(template)
            return template

    async def delete_book_template(self, template_id: UUID, user_id: UUID) -> bool:
        """Delete a book template."""
        async with get_session() as session:
            template = (
                await session.exec(
                    select(BookTemplate).where(BookTemplate.id == template_id, BookTemplate.user_id == user_id)
                )
            ).first()
            
            if not template:
                return False
            
            # System templates cannot be deleted by users
            if template.is_system:
                return False
            
            await session.delete(template)
            await session.commit()
            return True

    # Export methods
    async def export_book_to_pdf(self, book_id: UUID, user_id: UUID) -> Optional[bytes]:
        """Export a book to PDF."""
        # This is a placeholder for the actual implementation
        # In a real implementation, this would generate a PDF file
        book = await self.get_book_by_id(book_id, user_id)
        if not book:
            return None
        
        # Placeholder for PDF generation
        return b"PDF content"
