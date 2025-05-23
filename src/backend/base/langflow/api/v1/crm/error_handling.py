from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from typing import Any, Callable, TypeVar, ParamSpec, Awaitable
from functools import wraps
from loguru import logger

T = TypeVar("T")
P = ParamSpec("P")


def handle_exceptions(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
    """Decorator to handle exceptions in CRM endpoints consistently."""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            # Handle database integrity errors (e.g., unique constraint violations)
            logger.error(f"Database integrity error in {func.__name__}: {e}")
            if hasattr(kwargs.get("session", None), "rollback"):
                await kwargs["session"].rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Database constraint violation: {str(e)}",
            ) from e
        except HTTPException:
            # Re-raise HTTP exceptions as they are already properly formatted
            if hasattr(kwargs.get("session", None), "rollback"):
                await kwargs["session"].rollback()
            raise
        except Exception as e:
            # Handle all other exceptions
            logger.error(f"Unhandled error in {func.__name__}: {e}", exc_info=True)
            if hasattr(kwargs.get("session", None), "rollback"):
                await kwargs["session"].rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}",
            ) from e

    return wrapper


def get_http_status_code(status_code_name: str) -> int:
    """Get HTTP status code from status code name.
    
    This function ensures that we always have a valid status code even if the status import fails.
    """
    # Define common status codes
    status_codes = {
        "HTTP_200_OK": 200,
        "HTTP_201_CREATED": 201,
        "HTTP_204_NO_CONTENT": 204,
        "HTTP_400_BAD_REQUEST": 400,
        "HTTP_401_UNAUTHORIZED": 401,
        "HTTP_403_FORBIDDEN": 403,
        "HTTP_404_NOT_FOUND": 404,
        "HTTP_409_CONFLICT": 409,
        "HTTP_422_UNPROCESSABLE_ENTITY": 422,
        "HTTP_500_INTERNAL_SERVER_ERROR": 500,
    }
    
    # Try to get the status code from FastAPI's status module
    try:
        return getattr(status, status_code_name)
    except (AttributeError, TypeError):
        # Fallback to our dictionary if status import fails
        return status_codes.get(status_code_name, 500)  # Default to 500 if not found
