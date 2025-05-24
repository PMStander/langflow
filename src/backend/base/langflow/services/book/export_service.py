"""Export service for the Book Creator module."""

import io
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from langflow.services.book.pdf_generator import BookPDFGenerator
from langflow.services.database.models.book import Book, BookCover, BookInterior, BookPage, BookTemplate


class BookExportService:
    """Service for exporting books."""

    def __init__(self, session: AsyncSession):
        """Initialize the export service.
        
        Args:
            session: The database session
        """
        self.session = session

    async def get_book(self, book_id: UUID, user_id: UUID) -> Book:
        """Get a book by ID.
        
        Args:
            book_id: The book ID
            user_id: The user ID
            
        Returns:
            The book
            
        Raises:
            HTTPException: If the book is not found or the user doesn't have access
        """
        book = await self.session.get(Book, book_id)
        if not book or book.user_id != user_id:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    async def get_book_cover(self, book_id: UUID) -> Optional[BookCover]:
        """Get a book cover by book ID.
        
        Args:
            book_id: The book ID
            
        Returns:
            The book cover, or None if not found
        """
        return await self.session.get(BookCover, {"book_id": book_id})

    async def get_book_interior(self, book_id: UUID) -> Optional[BookInterior]:
        """Get a book interior by book ID.
        
        Args:
            book_id: The book ID
            
        Returns:
            The book interior, or None if not found
            
        Raises:
            HTTPException: If the book interior is not found
        """
        interior = await self.session.get(BookInterior, {"book_id": book_id})
        if not interior:
            raise HTTPException(status_code=404, detail="Book interior not found")
        return interior

    async def get_book_pages(self, book_id: UUID) -> List[BookPage]:
        """Get book pages by book ID.
        
        Args:
            book_id: The book ID
            
        Returns:
            The book pages
        """
        pages_query = await self.session.execute(
            f"SELECT * FROM book_page WHERE book_id = '{book_id}' ORDER BY page_number"
        )
        return pages_query.all()

    async def get_book_templates(self, template_ids: List[UUID]) -> Dict[UUID, BookTemplate]:
        """Get book templates by IDs.
        
        Args:
            template_ids: The template IDs
            
        Returns:
            A dictionary of templates by ID
        """
        if not template_ids:
            return {}
        
        templates_query = await self.session.execute(
            f"SELECT * FROM book_template WHERE id IN ({','.join([f'\\'{tid}\\'' for tid in template_ids])})"
        )
        templates = templates_query.all()
        return {template.id: template for template in templates}

    async def export_book_as_pdf(
        self,
        book_id: UUID,
        user_id: UUID,
        include_cover: bool = True,
        include_bleed: bool = False,
        quality: int = 300,
        format: str = "pdf",
    ) -> io.BytesIO:
        """Export a book as PDF.
        
        Args:
            book_id: The book ID
            user_id: The user ID
            include_cover: Whether to include the cover
            include_bleed: Whether to include bleed area
            quality: The quality of the PDF in DPI
            format: The export format (pdf, print-ready)
            
        Returns:
            A BytesIO object containing the PDF
            
        Raises:
            HTTPException: If the book is not found or the user doesn't have access
        """
        # Get book
        book = await self.get_book(book_id, user_id)
        
        # Get book cover if requested
        cover = None
        if include_cover:
            cover = await self.get_book_cover(book_id)
        
        # Get book interior
        interior = await self.get_book_interior(book_id)
        
        # Get book pages
        pages = await self.get_book_pages(book_id)
        
        # Get template IDs
        template_ids = []
        if interior and interior.template_id:
            template_ids.append(interior.template_id)
        
        for page in pages:
            if page.template_id:
                template_ids.append(page.template_id)
        
        # Get templates
        templates = await self.get_book_templates(template_ids)
        
        # Create PDF generator
        pdf_generator = BookPDFGenerator(
            book=book,
            cover=cover,
            interior=interior,
            pages=pages,
            templates=templates,
        )
        
        # Generate PDF
        if format == "print-ready":
            # For print-ready, always include bleed
            return pdf_generator.generate_pdf(include_bleed=True, quality=quality)
        else:
            return pdf_generator.generate_pdf(include_bleed=include_bleed, quality=quality)
