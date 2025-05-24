"""API endpoints for publishing books to print-on-demand services."""

from typing import Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from langflow.api.utils import CurrentActiveUser, DbSession
from langflow.services.book import BookExportService
from langflow.services.book.pod_service import get_pod_service
from langflow.services.database.models.book import Book

router = APIRouter(tags=["Book Publishing"], prefix="/books/{book_id}/publish")


class PublishBookRequest(BaseModel):
    """Request model for publishing a book."""
    
    service: str
    api_key: str
    include_cover: bool = True
    include_bleed: bool = True
    quality: int = 300
    metadata: Optional[Dict] = None


class PublishBookResponse(BaseModel):
    """Response model for publishing a book."""
    
    id: str
    status: str
    message: str
    details: Dict


@router.post("")
async def publish_book(
    book_id: UUID,
    request: PublishBookRequest,
    session: DbSession,
    current_user: CurrentActiveUser,
) -> PublishBookResponse:
    """Publish a book to a print-on-demand service.
    
    This endpoint publishes a book to a print-on-demand service like Amazon KDP or Lulu.
    It first exports the book as a PDF, then uploads it to the selected service.
    
    Args:
        book_id: The ID of the book to publish
        request: The publish request
        session: The database session
        current_user: The current user
        
    Returns:
        The response from the print-on-demand service
        
    Raises:
        HTTPException: If there's an error publishing the book
    """
    # Create export service
    export_service = BookExportService(session)
    
    # Get book
    book = await export_service.get_book(book_id, current_user.id)
    
    # Export book as PDF
    pdf_data = await export_service.export_book_as_pdf(
        book_id=book_id,
        user_id=current_user.id,
        include_cover=request.include_cover,
        include_bleed=request.include_bleed,
        quality=request.quality,
        format="print-ready",
    )
    
    # Create print-on-demand service
    try:
        pod_service = get_pod_service(request.service, request.api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Publish book
        response = await pod_service.publish_book(book, pdf_data)
        
        # Close the service client
        await pod_service.close()
        
        return PublishBookResponse(
            id=response["id"],
            status=response["status"],
            message=response["message"],
            details=response["details"],
        )
    except Exception as e:
        # Close the service client
        await pod_service.close()
        
        # Re-raise the exception
        raise


@router.get("/{publish_id}")
async def get_publish_status(
    book_id: UUID,
    publish_id: str,
    service: str = Query(..., description="The print-on-demand service"),
    api_key: str = Query(..., description="The API key for the service"),
    session: DbSession,
    current_user: CurrentActiveUser,
) -> PublishBookResponse:
    """Get the status of a published book.
    
    This endpoint gets the status of a book that has been published to a print-on-demand service.
    
    Args:
        book_id: The ID of the book
        publish_id: The ID of the published book on the service
        service: The print-on-demand service
        api_key: The API key for the service
        session: The database session
        current_user: The current user
        
    Returns:
        The status of the published book
        
    Raises:
        HTTPException: If there's an error getting the status
    """
    # Get book
    book = await session.get(Book, book_id)
    if not book or book.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Create print-on-demand service
    try:
        pod_service = get_pod_service(service, api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    try:
        # Get book status
        response = await pod_service.get_book_status(publish_id)
        
        # Close the service client
        await pod_service.close()
        
        return PublishBookResponse(
            id=response["id"],
            status=response["status"],
            message=response["message"],
            details=response["details"],
        )
    except Exception as e:
        # Close the service client
        await pod_service.close()
        
        # Re-raise the exception
        raise
