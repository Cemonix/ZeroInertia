import secrets
from collections.abc import Iterable
from typing import override

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.settings.app_settings import AppSettings

SAFE_METHODS: set[str] = {"GET", "HEAD", "OPTIONS", "TRACE"}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Simple double-submit-cookie CSRF protection.

    - For unsafe methods (POST, PUT, PATCH, DELETE), require header `X-CSRF-Token`
      to match the `csrf_token` cookie.
    - For safe methods, ensure a `csrf_token` cookie exists; if missing, set one.

    Notes:
    - Cookie is NOT HttpOnly so the frontend can read it and attach the header.
    - Cookie is SameSite=Lax which blocks most CSRF form posts while still allowing
      OAuth redirect flows. This middleware adds an explicit check for API writes.
    """

    def __init__(self, app: ASGIApp, exempt_paths: Iterable[str] | None = None) -> None:
        super().__init__(app)
        self.settings: AppSettings = AppSettings()
        self.exempt_paths: set[str] = set(exempt_paths or [])

    def _is_exempt(self, scope_path: str) -> bool:
        # Exact path matches; keep simple. Can be extended to prefixes if needed.
        return scope_path in self.exempt_paths

    @override
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if (
            self.settings.environment == "production"
            and not self._is_exempt(path)
            and request.method.upper() not in SAFE_METHODS
        ):
            cookie_token = request.cookies.get("csrf_token")
            header_token = request.headers.get("X-CSRF-Token") or request.headers.get("x-csrf-token")

            if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
                return Response(
                    status_code=403,
                    content=b'{"detail": "CSRF token missing or invalid"}',
                    media_type="application/json",
                )

        response = await call_next(request)

        # Issue CSRF cookie for safe methods if not present
        if request.method.upper() in SAFE_METHODS and not request.cookies.get("csrf_token"):
            token = secrets.token_urlsafe(32)
            # secure only in production
            secure = self.settings.environment == "production"
            response.set_cookie(
                key="csrf_token",
                value=token,
                max_age=60 * 60 * 24 * 7,  # 7 days
                secure=secure,
                httponly=False,  # must be readable by frontend
                samesite="lax",
            )

        return response

