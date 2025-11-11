"""Pagination schemas and utilities for consistent API responses."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

# Generic type for paginated items
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters for pagination requests."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Number of items per page (max 500)",
    )

    @field_validator("page")
    @classmethod
    def validate_page(cls, v: int) -> int:
        """Ensure page is at least 1."""
        if v < 1:
            raise ValueError("Page must be at least 1")
        return v

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """Ensure page_size is within reasonable bounds."""
        if v < 1:
            raise ValueError("Page size must be at least 1")
        if v > 500:
            raise ValueError("Page size must not exceed 500")
        return v

    @property
    def offset(self) -> int:
        """Calculate the offset for database queries."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Return the limit (page_size) for database queries."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T] = Field(description="List of items for the current page")
    total: int = Field(description="Total number of items across all pages")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """
        Create a paginated response from items and metadata.

        Args:
            items: List of items for the current page
            total: Total number of items across all pages
            page: Current page number (1-indexed)
            page_size: Number of items per page

        Returns:
            PaginatedResponse with calculated metadata
        """
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )


# Cursor-based pagination for future use
class CursorPaginationParams(BaseModel):
    """Query parameters for cursor-based pagination (for future infinite scroll)."""

    cursor: str | None = Field(
        default=None,
        description="Cursor for the next page (opaque token)",
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Number of items to return",
    )


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response (for future infinite scroll)."""

    items: list[T] = Field(description="List of items")
    next_cursor: str | None = Field(
        description="Cursor for the next page, null if no more pages"
    )
    has_next: bool = Field(description="Whether there are more items")
