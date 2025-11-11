"""FastAPI dependencies for pagination."""

from typing import Annotated

from fastapi import Query

from app.schemas.pagination import PaginationParams


async def get_pagination_params(
    page: Annotated[
        int,
        Query(
            ge=1,
            description="Page number (1-indexed)",
            examples=[1],
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=500,
            description="Number of items per page (max 500)",
            examples=[50],
        ),
    ] = 50,
) -> PaginationParams:
    """
    FastAPI dependency for extracting pagination parameters from query string.

    Args:
        page: Page number (1-indexed), default 1
        page_size: Number of items per page, default 50, max 500

    Returns:
        PaginationParams object with validated parameters

    Example:
        GET /api/v1/tasks?page=2&page_size=100
    """
    return PaginationParams(page=page, page_size=page_size)
