"""Parameter utilities for the API."""

from fastapi import Query
from fastapi_pagination import Params

MAX_PAGE_SIZE = 50
MIN_PAGE_SIZE = 1

def custom_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Page size"),
):
    """Custom pagination parameters."""
    return Params(page=page, size=size)
