"""Centralized exception handlers for FastAPI.

Maps custom application exceptions to appropriate HTTP responses.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    ServiceUnavailableException,
    UnauthorizedException,
)
from app.core.logging import logger


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all custom application exceptions and map them to appropriate HTTP status codes.

    This eliminates the need for string matching in API routes to determine status codes.
    """
    if not isinstance(exc, AppException):
        raise exc

    if isinstance(exc, NotFoundException):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, UnauthorizedException):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, ForbiddenException):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ConflictException):
        status_code = status.HTTP_409_CONFLICT
    elif isinstance(exc, ServiceUnavailableException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, BadRequestException):
        status_code = status.HTTP_400_BAD_REQUEST
    else:
        status_code = status.HTTP_400_BAD_REQUEST

    logger.warning(
        f"{exc.__class__.__name__} raised: {exc.message} | "
        + f"Path: {request.method} {request.url.path} | "
        + f"Status: {status_code}"
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message},
    )
