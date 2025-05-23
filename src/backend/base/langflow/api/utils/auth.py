"""Authentication utilities for the API."""

from typing import Annotated

from fastapi import Depends

from langflow.services.auth.utils import get_current_active_user, get_current_user
from langflow.services.database.models.user.model import User

# Type annotations for dependency injection
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
