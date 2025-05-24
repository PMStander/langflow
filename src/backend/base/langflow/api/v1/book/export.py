from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.book import BookExportService

router = APIRouter(tags=["Book Export"], prefix="/books/{book_id}/export")

@router.get("")
async def export_book(
    book_id: UUID,
    session: DbSession,
    current_user: CurrentActiveUser,
    format: str = Query("pdf", description="Export format (pdf, print-ready)"),
    quality: int = Query(300, description="Export quality in DPI"),
    include_cover: bool = Query(True, description="Include cover in export"),
    include_bleed: bool = Query(False, description="Include bleed area for printing"),
) -> StreamingResponse:
    """Export a book as PDF.

    This endpoint generates a PDF file for the specified book. The PDF can be customized
    with various options such as including the cover, adding bleed area for printing,
    and setting the quality.

    Args:
        book_id: The ID of the book to export
        session: The database session
        current_user: The current user
        format: The export format (pdf, print-ready)
        quality: The quality of the PDF in DPI
        include_cover: Whether to include the cover in the PDF
        include_bleed: Whether to include bleed area for printing

    Returns:
        A StreamingResponse containing the PDF file

    Raises:
        HTTPException: If the book is not found or the user doesn't have access
    """
    # Create export service
    export_service = BookExportService(session)

    # Export book as PDF
    buffer = await export_service.export_book_as_pdf(
        book_id=book_id,
        user_id=current_user.id,
        include_cover=include_cover,
        include_bleed=include_bleed,
        quality=quality,
        format=format,
    )

    # Get book name for filename
    book = await export_service.get_book(book_id, current_user.id)

    # Return PDF
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={book.name}.pdf"}
    )
