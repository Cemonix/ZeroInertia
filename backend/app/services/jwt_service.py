from datetime import datetime, timedelta, timezone
from typing import cast
from uuid import UUID

import jwt
from fastapi import HTTPException, status

from app.core.settings.app_settings import get_app_settings

settings = get_app_settings()


class JWTService:
    """Service for JWT token operations."""

    @staticmethod
    def create_access_token(user_id: UUID, email: str) -> str:
        """Create a JWT access token for a user."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
        payload = {
            "sub": str(user_id),  # Subject (user ID)
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        }

        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )

    @staticmethod
    def verify_token(token: str) -> dict[str, object]:
        """Verify and decode a JWT token."""
        try:
            payload = cast(dict[str, object], jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            ))

            # Validate token type
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            ) from None
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            ) from None
