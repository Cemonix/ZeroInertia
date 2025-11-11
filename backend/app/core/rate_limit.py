"""SlowAPI rate limiting setup and helpers.

Provides a configured Limiter instance, a key function that prefers the
authenticated user ID (falls back to client IP), and a dynamic limit helper
for routes that want different limits for authenticated vs anonymous calls.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_ipaddr

from ..services.jwt_service import JWTService
from .logging import logger
from .settings.app_settings import get_app_settings

settings = get_app_settings()

_limiter: Limiter | None = None

def _key_func(request: Request) -> str:
    """Rate limit key: prefer user ID if token present, else client IP.

    Returns a stable key per caller to scope limits correctly for authenticated users
    while still protecting anonymous traffic by IP.
    """
    try:
        token = request.cookies.get("__Host-access_token") or request.cookies.get("access_token")
        if token:
            payload = JWTService.verify_token(token)
            sub = payload.get("sub")
            if isinstance(sub, str) and sub:
                return f"user:{sub}"
    except Exception:
        # Fallback to IP on any token parsing/verification issue
        pass

    # get_ipaddr respects X-Forwarded-For headers for proxy support
    ip = get_ipaddr(request)
    return ip or "anonymous"


def auth_aware_limit(request: Request) -> str:
    """Return per-minute limit based on authentication state.

    Useful for route-level decorators, e.g.:
        @limiter.limit(auth_aware_limit)
    """
    per_min = settings.rate_limit_anon_per_min

    try:
        token = request.cookies.get("__Host-access_token") or request.cookies.get("access_token")
        if token:
            payload = JWTService.verify_token(token)
            if payload.get("sub"):
                per_min = settings.rate_limit_auth_per_min
    except Exception:
        # Treat as anonymous on any token issue
        per_min = settings.rate_limit_anon_per_min

    # Optional burst multiplier
    effective = max(1, int(per_min * settings.rate_limit_burst_multiplier))
    return f"{effective}/minute"


def _build_limiter() -> Limiter:
    """Build and configure a Limiter instance with settings."""
    kwargs: dict[str, object] = {
        "key_func": _key_func,
        "default_limits": [],  # No default limits - use decorators for granular control
        "headers_enabled": True,  # add X-RateLimit-* headers
    }
    if settings.rate_limit_storage_uri:
        # Use shared backend (e.g., Redis) if provided for multi-instance deployments
        kwargs["storage_uri"] = settings.rate_limit_storage_uri

    return Limiter(**kwargs)  # pyright: ignore[reportArgumentType]


async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    """Custom handler for rate limit exceeded errors with monitoring."""
    detail = exc.detail if isinstance(exc, RateLimitExceeded) else "Rate limit exceeded"

    # Calculate dynamic retry-after from exception
    retry_after = 60  # Default fallback
    if isinstance(exc, RateLimitExceeded):
        # SlowAPI doesn't expose retry_after directly, parse from detail if needed
        # For now, use 60 seconds as it matches our per-minute limits
        retry_after = 60

    # Log rate limit event for monitoring
    key = _key_func(request)
    logger.warning(
        f"Rate limit exceeded | path={request.url.path} | method={request.method} | key={key} | detail={detail}"
    )

    return JSONResponse(
        content={"detail": detail},
        status_code=429,
        headers={"Retry-After": str(retry_after)}
    )


def get_rate_limiter() -> Limiter:
    """Get the singleton Limiter instance."""
    global _limiter
    if _limiter is None:
        _limiter = _build_limiter()
    return _limiter
