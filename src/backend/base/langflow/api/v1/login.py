from __future__ import annotations

from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import select

from langflow.api.utils import DbSession
from langflow.api.v1.schemas import Token
from langflow.initial_setup.setup import get_or_create_default_folder
from langflow.services.auth.utils import (
    authenticate_user,
    create_refresh_token,
    create_user_longterm_token,
    create_user_tokens,
    get_password_hash,
)
from langflow.services.database.models.user.crud import get_user_by_id, get_user_by_username
from langflow.services.database.models.user.model import User
from langflow.services.deps import get_settings_service, get_supabase_auth_service, get_variable_service

router = APIRouter(tags=["Login"])


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/register", response_model=Token)
async def register_user(
    request: RegisterRequest,
    response: Response,
    db: DbSession,
):
    """Register a new user with Supabase Auth and internal database."""
    settings = get_settings_service().settings
    auth_settings = get_settings_service().auth_settings

    # Check if username already exists
    existing_user = await get_user_by_username(db, request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    # Create user in Supabase if enabled
    supabase_user = None
    if settings.supabase_auth_enabled:
        try:
            supabase_auth_service = get_supabase_auth_service()
            supabase_response = await supabase_auth_service.sign_up(
                request.username, request.password
            )
            if supabase_response and supabase_response.user:
                supabase_user = supabase_response.user
        except Exception as e:
            from loguru import logger
            logger.error(f"Error creating user in Supabase: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user in Supabase: {str(e)}",
            )

    # Create user in internal database
    try:
        # Check if this is the first user (should be superuser)
        stmt = select(User)
        users = (await db.exec(stmt)).all()
        is_first_user = len(users) == 0

        # Create the user
        hashed_password = get_password_hash(request.password)
        user = User(
            username=request.username,
            password=hashed_password,
            is_active=True,
            is_superuser=is_first_user,
            supabase_user_id=supabase_user.id if supabase_user else None,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Create tokens
        tokens = await create_user_tokens(user_id=user.id, db=db, update_last_login=True)

        # Set cookies
        response.set_cookie(
            "refresh_token_lf",
            tokens["refresh_token"],
            httponly=auth_settings.REFRESH_HTTPONLY,
            samesite=auth_settings.REFRESH_SAME_SITE,
            secure=auth_settings.REFRESH_SECURE,
            expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            "access_token_lf",
            tokens["access_token"],
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )

        # If using Supabase Auth, set Supabase tokens in cookies
        if supabase_user and settings.supabase_auth_enabled:
            # Get the current session
            session = await supabase_auth_service.get_session()
            if session and session.access_token:
                response.set_cookie(
                    "sb_access_token",
                    session.access_token,
                    httponly=False,  # Needs to be accessible by JavaScript
                    samesite=auth_settings.ACCESS_SAME_SITE,
                    secure=auth_settings.ACCESS_SECURE,
                    expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                    domain=auth_settings.COOKIE_DOMAIN,
                )
                response.set_cookie(
                    "sb_refresh_token",
                    session.refresh_token,
                    httponly=True,
                    samesite=auth_settings.REFRESH_SAME_SITE,
                    secure=auth_settings.REFRESH_SECURE,
                    expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
                    domain=auth_settings.COOKIE_DOMAIN,
                )

                # Add Supabase tokens to the response
                tokens["supabase_access_token"] = session.access_token
                tokens["supabase_refresh_token"] = session.refresh_token

        # Initialize user variables and create default folder
        await get_variable_service().initialize_user_variables(user.id, db)
        _ = await get_or_create_default_folder(db, user.id)

        return tokens
    except Exception as e:
        from loguru import logger
        logger.error(f"Error creating user: {e}")
        # Try to rollback the transaction
        await db.rollback()
        # If Supabase user was created, try to delete it
        if supabase_user and settings.supabase_auth_enabled:
            try:
                # TODO: Implement user deletion in Supabase
                pass
            except Exception as supabase_error:
                logger.error(f"Error deleting Supabase user: {supabase_error}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.post("/login", response_model=Token)
async def login_to_get_access_token(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    auth_settings = get_settings_service().auth_settings
    settings = get_settings_service().settings

    # Track if we're using Supabase Auth
    using_supabase_auth = False
    supabase_tokens = None

    try:
        user = await authenticate_user(form_data.username, form_data.password, db)

        # Check if this was authenticated via Supabase
        if settings.supabase_auth_enabled:
            from langflow.services.deps import get_supabase_auth_service

            try:
                supabase_auth_service = get_supabase_auth_service()
                # Get the current session if it exists
                session = await supabase_auth_service.get_session()
                if session and session.access_token:
                    using_supabase_auth = True
                    supabase_tokens = {
                        "access_token": session.access_token,
                        "refresh_token": session.refresh_token
                    }
            except Exception as e:
                # Just log the error but continue with internal auth
                from loguru import logger
                logger.debug(f"Error getting Supabase session: {e}")

    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    if user:
        tokens = await create_user_tokens(user_id=user.id, db=db, update_last_login=True)

        # Set internal auth cookies
        response.set_cookie(
            "refresh_token_lf",
            tokens["refresh_token"],
            httponly=auth_settings.REFRESH_HTTPONLY,
            samesite=auth_settings.REFRESH_SAME_SITE,
            secure=auth_settings.REFRESH_SECURE,
            expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            "access_token_lf",
            tokens["access_token"],
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            "apikey_tkn_lflw",
            str(user.store_api_key),
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=None,  # Set to None to make it a session cookie
            domain=auth_settings.COOKIE_DOMAIN,
        )

        # If using Supabase Auth, set Supabase tokens in cookies
        if using_supabase_auth and supabase_tokens:
            response.set_cookie(
                "sb_access_token",
                supabase_tokens["access_token"],
                httponly=False,  # Needs to be accessible by JavaScript
                samesite=auth_settings.ACCESS_SAME_SITE,
                secure=auth_settings.ACCESS_SECURE,
                expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                domain=auth_settings.COOKIE_DOMAIN,
            )
            response.set_cookie(
                "sb_refresh_token",
                supabase_tokens["refresh_token"],
                httponly=True,
                samesite=auth_settings.REFRESH_SAME_SITE,
                secure=auth_settings.REFRESH_SECURE,
                expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
                domain=auth_settings.COOKIE_DOMAIN,
            )

            # Add Supabase tokens to the response
            tokens["supabase_access_token"] = supabase_tokens["access_token"]
            tokens["supabase_refresh_token"] = supabase_tokens["refresh_token"]

        await get_variable_service().initialize_user_variables(user.id, db)
        # Create default project for user if it doesn't exist
        _ = await get_or_create_default_folder(db, user.id)
        return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/auto_login")
async def auto_login(response: Response, db: DbSession):
    auth_settings = get_settings_service().auth_settings

    if auth_settings.AUTO_LOGIN:
        user_id, tokens = await create_user_longterm_token(db)
        response.set_cookie(
            "access_token_lf",
            tokens["access_token"],
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=None,  # Set to None to make it a session cookie
            domain=auth_settings.COOKIE_DOMAIN,
        )

        user = await get_user_by_id(db, user_id)

        if user:
            if user.store_api_key is None:
                user.store_api_key = ""

            response.set_cookie(
                "apikey_tkn_lflw",
                str(user.store_api_key),  # Ensure it's a string
                httponly=auth_settings.ACCESS_HTTPONLY,
                samesite=auth_settings.ACCESS_SAME_SITE,
                secure=auth_settings.ACCESS_SECURE,
                expires=None,  # Set to None to make it a session cookie
                domain=auth_settings.COOKIE_DOMAIN,
            )

        return tokens

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "message": "Auto login is disabled. Please enable it in the settings",
            "auto_login": False,
        },
    )


@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    db: DbSession,
):
    auth_settings = get_settings_service().auth_settings

    token = request.cookies.get("refresh_token_lf")

    if token:
        tokens = await create_refresh_token(token, db)
        response.set_cookie(
            "refresh_token_lf",
            tokens["refresh_token"],
            httponly=auth_settings.REFRESH_HTTPONLY,
            samesite=auth_settings.REFRESH_SAME_SITE,
            secure=auth_settings.REFRESH_SECURE,
            expires=auth_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )
        response.set_cookie(
            "access_token_lf",
            tokens["access_token"],
            httponly=auth_settings.ACCESS_HTTPONLY,
            samesite=auth_settings.ACCESS_SAME_SITE,
            secure=auth_settings.ACCESS_SECURE,
            expires=auth_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            domain=auth_settings.COOKIE_DOMAIN,
        )
        return tokens
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/logout")
async def logout(response: Response):
    settings = get_settings_service().settings

    # Delete internal auth cookies
    response.delete_cookie("refresh_token_lf")
    response.delete_cookie("access_token_lf")
    response.delete_cookie("apikey_tkn_lflw")

    # Delete Supabase Auth cookies if enabled
    if settings.supabase_auth_enabled:
        response.delete_cookie("sb_access_token")
        response.delete_cookie("sb_refresh_token")

        # Sign out from Supabase Auth
        try:
            from langflow.services.deps import get_supabase_auth_service

            supabase_auth_service = get_supabase_auth_service()
            await supabase_auth_service.sign_out()
        except Exception as e:
            # Just log the error but continue with logout
            from loguru import logger
            logger.debug(f"Error signing out from Supabase Auth: {e}")

    return {"message": "Logout successful"}
