from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.seed import create_inbox_project
from app.models.user import User


class UserService:
    """Service for user-related operations."""

    @staticmethod
    async def get_user_by_oauth(
        session: AsyncSession,
        oauth_provider: str,
        oauth_subject_id: str
    ) -> User | None:
        """Get user by OAuth provider and subject ID."""
        stmt = select(User).where(
            User.oauth_provider == oauth_provider,
            User.oauth_subject_id == oauth_subject_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
        """Get user by ID."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(
        session: AsyncSession,
        oauth_provider: str,
        oauth_subject_id: str,
        email: str,
        full_name: str | None = None,
        avatar_url: str | None = None
    ) -> User:
        """Create a new user."""
        user = User(
            oauth_provider=oauth_provider,
            oauth_subject_id=oauth_subject_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        _ = await create_inbox_project(session, user.id)

        return user

    @staticmethod
    async def update_user(
        session: AsyncSession,
        user: User,
        email: str | None = None,
        full_name: str | None = None,
        avatar_url: str | None = None
    ) -> User:
        """Update an existing user."""
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url

        user.last_login_at = func.now()

        await session.commit()
        await session.refresh(user)
        return user
