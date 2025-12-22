from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Book
from app.schemas.media import BookCreate, BookUpdate, CSVImportResult
from app.services.base_service import apply_updates_async
from app.services.genre_service import get_genres_by_ids
from app.services.media_service.base import (
    delete_media,
    get_all_by_user,
    get_by_id,
    reload_media_with_genres,
)
from app.services.media_service.csv_import_service import import_csv_generic

# pyright: reportAny=false

async def create_book(
    db: AsyncSession,
    user_id: UUID,
    book_data: BookCreate,
) -> Book:
    """Create a new book for the given user."""
    data = book_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    book = Book(**data)

    if book_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, book_data.genre_ids)
        book.genres = list(genres)

    db.add(book)
    await db.commit()
    return await reload_media_with_genres(db, book.id, user_id, Book)


async def get_book_by_id(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> Book | None:
    """Return a specific book for the user."""
    return await get_by_id(db, book_id, user_id, Book)


async def get_all_books(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Book]:
    """Return all books for the user."""
    return await get_all_by_user(db, user_id, Book)


async def update_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    book_data: BookUpdate,
) -> Book:
    """Update the book with the supplied fields."""
    book = await get_by_id(db, book_id, user_id, Book)
    if book is None:
        raise MediaNotFoundException(str(book_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                book.status = value
            else:
                book.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            book.genres = list(genres)

    _ = await apply_updates_async(
        model=book,
        update_schema=book_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(book)
    await db.commit()
    return await reload_media_with_genres(db, book.id, user_id, Book)


async def delete_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a book."""
    await delete_media(db, book_id, user_id, Book)


async def import_books_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import books from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Book,
        create_schema=BookCreate,
    )
