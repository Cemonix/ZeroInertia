"""Redis service for caching and session management."""

import secrets
from typing import cast

import redis.asyncio as redis
from redis.exceptions import ConnectionError, RedisError

from app.core.settings.app_settings import get_app_settings

settings = get_app_settings()


class OAuthStateError(Exception):
    """Custom exception for OAuth state errors."""
    pass


class RedisService:
    """Service for Redis operations."""

    _client: redis.Redis | None = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get Redis client instance."""
        if cls._client is None:
            cls._client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close Redis connection."""
        if cls._client:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def health_check(cls) -> bool:
        """Check Redis connection."""
        try:
            client = await cls.get_client()
            return await client.ping()  # pyright: ignore[reportAny, reportUnknownMemberType]
        except (ConnectionError, RedisError):
            return False


class OAuthStateService:
    """Service for managing OAuth state tokens with Redis."""

    STATE_PREFIX: str = "zero_inertia:oauth_state:"
    STATE_EXPIRY: int = 600  # 10 minutes

    @classmethod
    async def generate_state(cls) -> str:
        """Generate and store OAuth state token."""
        state = secrets.token_urlsafe(32)

        try:
            client = await RedisService.get_client()
            await client.setex(
                f"{cls.STATE_PREFIX}{state}",
                cls.STATE_EXPIRY,
                "valid"
            )
            return state
        except RedisError as e:
            raise OAuthStateError(f"Failed to store OAuth state: {e}") from e

    @classmethod
    async def validate_state(cls, state: str) -> bool:
        """Validate and consume OAuth state token."""
        if not state:
            return False

        try:
            client = await RedisService.get_client()
            key = f"{cls.STATE_PREFIX}{state}"

            # Check if state exists and delete it (one-time use)
            result = await client.delete(key)  # pyright: ignore[reportAny]
            if isinstance(result, int):
                return result == 1
            return False

        except RedisError:
            return False

    @classmethod
    async def cleanup_expired_states(cls) -> int:
        """Clean up expired OAuth states (optional maintenance task)."""
        try:
            client = await RedisService.get_client()
            pattern = f"{cls.STATE_PREFIX}*"

            # Get all OAuth state keys
            keys = cast(list[str], await client.keys(pattern))  # pyright: ignore[reportUnknownMemberType]

            # Redis TTL handles expiration automatically, but we can
            # manually check for any orphaned keys
            cleaned = 0
            for key in keys:
                ttl = cast(int, await client.ttl(key))
                if ttl == -1:  # Key exists but has no expiration
                    await client.delete(key)
                    cleaned += 1

            return cleaned

        except RedisError:
            return 0
