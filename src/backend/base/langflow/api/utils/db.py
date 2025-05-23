"""Database utilities for the API."""

from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.services.deps import get_session

# Type annotations for dependency injection
DbSession = Annotated[AsyncSession, Depends(get_session)]
