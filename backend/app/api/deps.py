from uuid import UUID

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.services.jwt_service import JWTService
from app.services.user_service import UserService


async def get_current_user(
    access_token: str = Cookie(None),  # pyright: ignore[reportCallInDefaultInitializer]
    session: AsyncSession = Depends(get_db)  # noqa: B008  # pyright: ignore[reportCallInDefaultInitializer]
) -> User:
    """Get the current authenticated user from JWT cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Verify JWT token
    payload = JWTService.verify_token(access_token)

    # Extract user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        ) from None

    # Get user from database
    user = await UserService.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


async def get_current_user_optional(
    access_token: str = Cookie(None),  # pyright: ignore[reportCallInDefaultInitializer]
    session: AsyncSession = Depends(get_db)  # noqa: B008  # pyright: ignore[reportCallInDefaultInitializer]
) -> User | None:
    """Get the current authenticated user, or None if not authenticated."""
    try:
        return await get_current_user(access_token, session)
    except HTTPException:
        return None
