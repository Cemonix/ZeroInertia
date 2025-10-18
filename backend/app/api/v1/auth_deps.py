from typing import cast
from uuid import UUID

import httpx
from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings.app_settings import AppSettings
from app.models.user import User
from app.services.jwt_service import JWTService
from app.services.user_service import UserService

settings = AppSettings()


async def exchange_code_for_token(code: str) -> str:
    """Exchange authorization code for access token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'client_id': settings.google_client_id,
                    'client_secret': settings.google_client_secret,
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': settings.oauth_redirect_uri,
                },
                headers={'Accept': 'application/json'}
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Token exchange failed: {response.status_code}"
                )

            token_data = cast(dict[str, object], response.json())
            access_token = token_data.get('access_token')

            if access_token is None or not isinstance(access_token, str):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received from Google"
                )

            return access_token

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to connect to Google OAuth service"
            ) from e


async def fetch_user_info(access_token: str) -> dict[str, str | None]:
    """Fetch user information from Google using access token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Accept': 'application/json'
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to fetch user info: {response.status_code}"
                )

            return cast(dict[str, str | None], response.json())

        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch user information from Google"
            ) from e


async def create_or_update_user(session: AsyncSession, user_data: dict[str, str | None]) -> User:
    """
    Create or update user in database.
    Check if user exists, update if so, otherwise create new.

    params:
        session: Database session
        user_data: User data from Google

    returns: User object
    """

    oauth_subject_id = user_data.get('id')
    email = user_data.get('email')
    full_name = user_data.get('name')
    avatar_url = user_data.get('picture')

    if oauth_subject_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incomplete user data received from Google"
        )

    user = await UserService.get_user_by_oauth(session, 'google', str(oauth_subject_id))

    if user is not None:
        # Update existing user
        user = await UserService.update_user(
            session,
            user,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url
        )
    else:
        # Create new user
        user = await UserService.create_user(
            session,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
            oauth_provider='google',
            oauth_subject_id=str(oauth_subject_id)
        )

    return user


async def get_current_user_id(request: Request) -> UUID:
    """Extract user ID from JWT cookie."""
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    payload = JWTService.verify_token(access_token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    try:
        return UUID(str(user_id_str))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        ) from None
