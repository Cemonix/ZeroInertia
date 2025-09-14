import secrets
from typing import cast
from urllib.parse import urlencode

import httpx
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import logger
from app.core.settings.app_settings import AppSettings
from app.services.jwt_service import JWTService
from app.services.user_service import UserService

# Load settings
app_settings = AppSettings()  # pyright: ignore[reportCallIssue]

# Initialize OAuth
oauth = OAuth()
_ = cast(OAuth, oauth.register(  # pyright: ignore[reportUnknownMemberType]
    name='google',
    client_id=app_settings.google_client_id,
    client_secret=app_settings.google_client_secret,
    server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
))

router = APIRouter()


@router.get("/google/login")
async def google_login(request: Request) -> dict[str, str]:
    """Initiate Google OAuth login."""
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session
    # TODO: In production, use a more robust session management solution like Redis or database-backed sessions
    request.session['oauth_state'] = state

    # Build Google OAuth URL
    params = {
        'client_id': app_settings.google_client_id,
        'redirect_uri': app_settings.oauth_redirect_uri,
        'scope': 'openid email profile',
        'response_type': 'code',
        'state': state,
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    return {"auth_url": google_auth_url}


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    code: str,
    state: str,
    session: AsyncSession = Depends(get_db),  # noqa: B008  # pyright: ignore[reportCallInDefaultInitializer]
) -> dict[str, str | dict[str, str | None]]:
    """Handle Google OAuth callback."""
    # Verify state to prevent CSRF
    stored_state = request.session.get('oauth_state')
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    # Exchange authorization code for access token
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': app_settings.google_client_id,
                    'client_secret': app_settings.google_client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': app_settings.oauth_redirect_uri,
                }
            )

            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )

            token_data = cast(dict[str, str], token_response.json())
            access_token = token_data.get('access_token')

            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received"
                )

            # Get user info from Google
            user_response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )

            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to get user info from Google"
                )

            user_data = cast(dict[str, str], user_response.json())

    except httpx.RequestError as e:
        logger.error(f"HTTP request failed during OAuth: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth request failed"
        ) from None

    # Create or update user in database
    existing_user = await UserService.get_user_by_oauth(
        session=session,
        oauth_provider="google",
        oauth_subject_id=user_data['id']
    )

    if existing_user:
        user = await UserService.update_user(
            session=session,
            user=existing_user,
            email=user_data['email'],
            full_name=user_data.get('name'),
            avatar_url=user_data.get('picture')
        )
    else:
        user = await UserService.create_user(
            session=session,
            oauth_provider="google",
            oauth_subject_id=user_data['id'],
            email=user_data['email'],
            full_name=user_data.get('name'),
            avatar_url=user_data.get('picture')
        )

    # Create JWT token
    jwt_token = JWTService.create_access_token(
        user_id=user.id,
        email=user.email
    )

    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        secure=app_settings.environment == "production",
        samesite="strict",
        max_age=app_settings.jwt_expire_minutes * 60
    )

    # Clear OAuth state
    request.session.pop('oauth_state', None)

    logger.info(f"User {user.email} successfully authenticated via Google OAuth")

    return {
        "message": "Authentication successful",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        }
    }


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the JWT cookie."""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}
