"""Supabase Auth Service for Langflow.

This module provides the Supabase Auth Service that integrates with Supabase Auth
while preserving the existing authentication system.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any, Dict, Optional, TYPE_CHECKING, Tuple
from uuid import UUID

from loguru import logger
from sqlmodel import select
from supabase import Client, create_client

from langflow.services.base import Service

if TYPE_CHECKING:
    from langflow.services.settings.service import SettingsService
    from langflow.services.database.models.user.model import User


class SupabaseAuthService(Service):
    """Service for handling Supabase Auth operations."""

    name = "supabase_auth_service"

    def __init__(self, settings_service: "SettingsService"):
        """Initialize the Supabase Auth Service.

        Args:
            settings_service: The settings service.
        """
        self.settings_service = settings_service
        self.supabase_url = None
        self.supabase_key = None
        self.supabase_client = None
        self.initialize_client()

    def initialize_client(self) -> None:
        """Initialize the Supabase client."""
        try:
            # Get Supabase URL and key from environment variables
            self.supabase_url = self.settings_service.settings.supabase_url
            self.supabase_key = self.settings_service.settings.supabase_key

            if not self.supabase_url or not self.supabase_key:
                logger.warning("Supabase URL or key not set. Supabase Auth will not be available.")
                return

            # Create Supabase client
            self.supabase_client = create_client(self.supabase_url, self.supabase_key)
            logger.info("Supabase Auth client initialized successfully.")
        except Exception as e:
            logger.exception(f"Error initializing Supabase client: {e}")
            self.supabase_client = None

    def is_enabled(self) -> bool:
        """Check if Supabase Auth is enabled.

        Returns:
            bool: True if Supabase Auth is enabled, False otherwise.
        """
        return self.supabase_client is not None

    async def sign_up(self, email: str, password: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Sign up a new user with Supabase Auth.

        Args:
            email: The user's email.
            password: The user's password.
            metadata: Additional user metadata.

        Returns:
            Dict[str, Any]: The response from Supabase Auth.
        """
        if not self.is_enabled():
            raise ValueError("Supabase Auth is not enabled.")

        try:
            options = {"data": metadata} if metadata else None
            response = self.supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": options
            })
            return response
        except Exception as e:
            logger.exception(f"Error signing up user with Supabase Auth: {e}")
            raise

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in a user with Supabase Auth.

        Args:
            email: The user's email.
            password: The user's password.

        Returns:
            Dict[str, Any]: The response from Supabase Auth.
        """
        if not self.is_enabled():
            raise ValueError("Supabase Auth is not enabled.")

        try:
            response = self.supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            logger.exception(f"Error signing in user with Supabase Auth: {e}")
            raise

    async def get_user(self, jwt: Optional[str] = None) -> Dict[str, Any]:
        """Get the current user from Supabase Auth.

        Args:
            jwt: Optional JWT token.

        Returns:
            Dict[str, Any]: The user data.
        """
        if not self.is_enabled():
            raise ValueError("Supabase Auth is not enabled.")

        try:
            response = self.supabase_client.auth.get_user(jwt)
            return response
        except Exception as e:
            logger.exception(f"Error getting user from Supabase Auth: {e}")
            raise

    async def sign_out(self) -> None:
        """Sign out the current user from Supabase Auth."""
        if not self.is_enabled():
            raise ValueError("Supabase Auth is not enabled.")

        try:
            self.supabase_client.auth.sign_out()
        except Exception as e:
            logger.exception(f"Error signing out user from Supabase Auth: {e}")
            raise

    async def sync_user_to_internal(self, supabase_user: Dict[str, Any], is_superuser: bool = False) -> "User":
        """Sync a Supabase user to the internal database.

        Args:
            supabase_user: The Supabase user data.
            is_superuser: Whether the user should be a superuser.

        Returns:
            User: The internal user.
        """
        from langflow.services.auth.utils import get_password_hash
        from langflow.services.database.models.user.crud import get_user_by_username
        from langflow.services.database.models.user.model import User, UserUpdate
        from langflow.initial_setup.setup import get_or_create_default_folder

        if not supabase_user or "id" not in supabase_user:
            raise ValueError("Invalid Supabase user data")

        supabase_id = supabase_user["id"]
        email = supabase_user.get("email")

        if not email:
            raise ValueError("Supabase user has no email")

        # Check if user already exists with this Supabase ID
        async with self.settings_service.db_service.with_session() as db:
            # First, try to find by Supabase ID
            stmt = select(User).where(User.supabase_user_id == supabase_id)
            user = (await db.exec(stmt)).first()

            if not user:
                # Try to find by email/username
                user = await get_user_by_username(db, email)

                if user:
                    # User exists but doesn't have Supabase ID yet, update it
                    user_update = UserUpdate(supabase_user_id=supabase_id)
                    for attr, value in user_update.model_dump(exclude_unset=True).items():
                        if hasattr(user, attr) and value is not None:
                            setattr(user, attr, value)

                    user.updated_at = datetime.now(timezone.utc)
                    await db.commit()
                else:
                    # Create new user
                    # Generate a random password since auth will be handled by Supabase
                    random_password = secrets.token_urlsafe(32)
                    hashed_password = get_password_hash(random_password)

                    user = User(
                        username=email,
                        password=hashed_password,
                        supabase_user_id=supabase_id,
                        is_active=True,
                        is_superuser=is_superuser,
                    )

                    db.add(user)
                    await db.commit()
                    await db.refresh(user)

                    # Create default folder for the user
                    folder = await get_or_create_default_folder(db, user.id)
                    if not folder:
                        logger.error(f"Error creating default folder for user {user.id}")

        return user

    async def get_session(self) -> Dict[str, Any]:
        """Get the current session from Supabase Auth.

        Returns:
            Dict[str, Any]: The session data.
        """
        if not self.is_enabled():
            raise ValueError("Supabase Auth is not enabled.")

        try:
            response = self.supabase_client.auth.get_session()
            return response
        except Exception as e:
            logger.exception(f"Error getting session from Supabase Auth: {e}")
            raise
