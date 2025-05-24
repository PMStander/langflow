"""Models for CRM API endpoints."""
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginationMetadata(BaseModel):
    """Metadata for paginated responses."""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number (1-based)")
    size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number")
    prev_page: Optional[int] = Field(None, description="Previous page number")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    items: List[T] = Field(..., description="List of items")
    metadata: PaginationMetadata = Field(..., description="Pagination metadata")
