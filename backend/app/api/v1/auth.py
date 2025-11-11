"""Authentication routes using Google OAuth with redirect flow."""
import secrets
from typing import cast
from urllib.parse import urlencode
from uuid import UUID

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.api.v1.auth_deps import (
    create_or_update_user,
    exchange_code_for_token,
    fetch_user_info,
)
from app.core.database import get_db
from app.core.exceptions import InvalidTokenException, UnauthorizedException
from app.core.rate_limit import auth_aware_limit, get_rate_limiter
from app.core.settings.app_settings import AppSettings
from app.schemas.user import UserResponse
from app.services.jwt_service import JWTService
from app.services.redis_service import OAuthStateService
from app.services.user_service import UserService

# pyright: reportUnknownMemberType=false, reportUntypedFunctionDecorator=false

# Load settings
settings = AppSettings()

# Initialize rate limiter
limiter = get_rate_limiter()

# Initialize OAuth
oauth = OAuth()
_ = cast(OAuth, oauth.register(
    name='google',
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
))

router = APIRouter()


@limiter.limit("10/minute")
@router.get("/google/login")
async def google_login(request: Request) -> RedirectResponse:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    """Initiate Google OAuth login with redirect flow."""
    state = await OAuthStateService.generate_state()

    # Build Google OAuth URL
    params = {
        'client_id': settings.google_client_id,
        'redirect_uri': settings.oauth_redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return RedirectResponse(url=google_auth_url, status_code=302)


@router.get("/google/callback")
async def google_callback(
    request: Request,  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    code: str,
    state: str,
    session: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Handle Google OAuth callback with redirect flow."""
    try:
        # Verify state to prevent CSRF attacks
        is_valid_state = await OAuthStateService.validate_state(state)
        if not is_valid_state:
            return RedirectResponse(
                url=f"{settings.cors_origins[0]}/auth/error?message=Invalid+state",
                status_code=302
            )

        access_token = await exchange_code_for_token(code)
        user_data = await fetch_user_info(access_token)
        user = await create_or_update_user(session, user_data)

        jwt_token = JWTService.create_access_token(user_id=user.id, email=user.email)

        # Create secure response with JWT cookie and redirect to frontend
        response = RedirectResponse(
            url=f"{settings.cors_origins[0]}/home",
            status_code=302
        )

        # Set secure JWT cookie
        # In production, use __Host- prefix (requires Secure + Path=/ and no Domain)
        # In development (HTTP), browsers reject __Host- without Secure, so use a plain name
        cookie_name = "__Host-access_token" if settings.environment == "production" else "access_token"
        response.set_cookie(
            key=cookie_name,
            value=jwt_token,
            max_age=settings.jwt_expire_minutes * 60,
            httponly=True,  # Prevents XSS
            secure=settings.environment == "production",  # Always enforce HTTPS in production
            samesite="lax",  # Allows cookie on top-level GET navigations (needed for OAuth redirect)
            domain=None,  # Current domain only
            path="/"  # Required for __Host- prefix in production
        )

        # Rotate CSRF token on login (double submit cookie pattern)
        csrf_token = secrets.token_urlsafe(32)
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            max_age=settings.jwt_expire_minutes * 60,
            httponly=False,  # must be readable by frontend
            secure=settings.environment == "production",
            samesite="lax",
            domain=None,
        )

        return response

    except HTTPException as e:
        logger.warning(
            f"OAuth authentication failed: {e.detail} | " +
            f"state={state} | status_code={e.status_code}"
        )
        return RedirectResponse(
            url=f"{settings.cors_origins[0]}/auth/error?message=Authentication+failed",
            status_code=302
        )
    except Exception:
        logger.exception(
            f"Unexpected OAuth error | state={state} | " +
            f"code_prefix={code[:10] if code else None}"
        )
        return RedirectResponse(
            url=f"{settings.cors_origins[0]}/auth/error?message=System+error",
            status_code=302
        )


@limiter.limit(auth_aware_limit)
@router.get("/me")
async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get the currently authenticated user from cookie."""
    # Get JWT from cookie
    access_token = request.cookies.get("__Host-access_token") or request.cookies.get("access_token")
    if not access_token:
        raise UnauthorizedException("Access token missing")

    payload = JWTService.verify_token(access_token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload")

    try:
        user_id = UUID(str(user_id_str))
    except ValueError as e:
        raise InvalidTokenException("Invalid user ID in token") from e

    # Get user from database
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise UnauthorizedException("User not found")

    return UserResponse.model_validate(user)


@limiter.limit(auth_aware_limit)
@router.get("/is_authenticated")
async def is_authenticated(
    request: Request
) -> JSONResponse:
    """Check if the user is authenticated."""
    access_token = request.cookies.get("__Host-access_token") or request.cookies.get("access_token")
    if not access_token:
        return JSONResponse({"is_authenticated": False})

    try:
        payload = JWTService.verify_token(access_token)
        user_id = payload.get("sub")
        if not user_id:
            return JSONResponse({"is_authenticated": False})

        return JSONResponse({"is_authenticated": True})
    except Exception:
        return JSONResponse({"is_authenticated": False})


@limiter.limit(auth_aware_limit)
@router.post("/logout")
async def logout(request: Request) -> JSONResponse:  # noqa: ARG001  # pyright: ignore[reportUnusedParameter]
    """Logout user by clearing the JWT cookie."""
    response = JSONResponse({"message": "Successfully logged out"})
    # Delete both possible cookie names
    response.delete_cookie(key="__Host-access_token", path="/")
    response.delete_cookie(key="access_token", path="/")
    # Also clear CSRF token on logout
    response.delete_cookie(key="csrf_token")
    return response
