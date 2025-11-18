from collections.abc import Sequence
from datetime import date
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Book, Game, Movie, Show
from app.schemas.media import (
    BookCreate,
    BookUpdate,
    GameCreate,
    GameUpdate,
    MovieCreate,
    MovieUpdate,
    ShowCreate,
    ShowUpdate,
)
from app.services.base_service import apply_updates_async

MediaModel = TypeVar("MediaModel", Book, Game, Movie, Show)

# pyright: reportAny=false

# ===== Generic Service Functions =====


async def get_all_by_user(
    db: AsyncSession,
    user_id: UUID,
    model: type[MediaModel],
) -> Sequence[MediaModel]:
    """Get all media of a specific type for a user"""
    result = await db.execute(
        select(model)
        .where(model.user_id == user_id)
        .order_by(model.created_at.desc())
    )
    return result.scalars().all()


async def get_by_id(
    db: AsyncSession,
    media_id: UUID,
    user_id: UUID,
    model: type[MediaModel],
) -> MediaModel | None:
    """Get a specific media item by ID"""
    result = await db.execute(
        select(model).where(model.id == media_id, model.user_id == user_id)
    )
    return result.scalars().first()


async def get_by_status(
    db: AsyncSession,
    user_id: UUID,
    model: type[MediaModel],
    status: str,
) -> Sequence[MediaModel]:
    """Filter media by status"""
    result = await db.execute(
        select(model)
        .where(model.user_id == user_id, model.status == status)
        .order_by(model.created_at.desc())
    )
    return result.scalars().all()


async def create_media(
    db: AsyncSession,
    model: type[MediaModel],
    data: dict[str, object],
) -> MediaModel:
    """Generic create for any media type"""
    media_item = model(**data)
    db.add(media_item)
    await db.commit()
    await db.refresh(media_item)
    return media_item


async def update_media(
    db: AsyncSession,
    media_id: UUID,
    user_id: UUID,
    model: type[MediaModel],
    update_schema: BaseModel,
) -> MediaModel:
    """Generic update for any media type"""
    media = await get_by_id(db, media_id, user_id, model)
    if media is None:
        raise MediaNotFoundException(str(media_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                media.status = value
            else:
                media.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType, reportAttributeAccessIssue]

    _ = await apply_updates_async(
        model=media,
        update_schema=update_schema,
        custom_handlers={"status": handle_status}
    )

    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


async def delete_media(
    db: AsyncSession,
    media_id: UUID,
    user_id: UUID,
    model: type[MediaModel],
) -> None:
    """Generic delete for any media type"""
    media = await get_by_id(db, media_id, user_id, model)
    if media is None:
        raise MediaNotFoundException(str(media_id))

    await db.delete(media)
    await db.commit()


# ===== Book Service Functions =====


async def create_book(
    db: AsyncSession,
    user_id: UUID,
    book_data: BookCreate,
) -> Book:
    """Create a new book for the given user."""
    data = book_data.model_dump()
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    return await create_media(db, Book, data)


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
    return await update_media(db, book_id, user_id, Book, book_data)


async def delete_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a book."""
    await delete_media(db, book_id, user_id, Book)


# ===== Movie Service Functions =====


async def create_movie(
    db: AsyncSession,
    user_id: UUID,
    movie_data: MovieCreate,
) -> Movie:
    """Create a new movie for the given user."""
    data = movie_data.model_dump()
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    return await create_media(db, Movie, data)


async def get_movie_by_id(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
) -> Movie | None:
    """Return a specific movie for the user."""
    return await get_by_id(db, movie_id, user_id, Movie)


async def get_all_movies(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Movie]:
    """Return all movies for the user."""
    return await get_all_by_user(db, user_id, Movie)


async def update_movie(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
    movie_data: MovieUpdate,
) -> Movie:
    """Update the movie with the supplied fields."""
    return await update_media(db, movie_id, user_id, Movie, movie_data)


async def delete_movie(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a movie."""
    await delete_media(db, movie_id, user_id, Movie)


# ===== Game Service Functions =====


async def create_game(
    db: AsyncSession,
    user_id: UUID,
    game_data: GameCreate,
) -> Game:
    """Create a new game for the given user."""
    data = game_data.model_dump()
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    return await create_media(db, Game, data)


async def get_game_by_id(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> Game | None:
    """Return a specific game for the user."""
    return await get_by_id(db, game_id, user_id, Game)


async def get_all_games(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Game]:
    """Return all games for the user."""
    return await get_all_by_user(db, user_id, Game)


async def update_game(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
    game_data: GameUpdate,
) -> Game:
    """Update the game with the supplied fields."""
    return await update_media(db, game_id, user_id, Game, game_data)


async def delete_game(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a game."""
    await delete_media(db, game_id, user_id, Game)


# ===== Show Service Functions =====


async def create_show(
    db: AsyncSession,
    user_id: UUID,
    show_data: ShowCreate,
) -> Show:
    """Create a new TV show season for the given user."""
    data = show_data.model_dump()
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value
    return await create_media(db, Show, data)


async def get_show_by_id(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
) -> Show | None:
    """Return a specific show for the user."""
    return await get_by_id(db, show_id, user_id, Show)


async def get_all_shows(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Show]:
    """Return all shows for the user."""
    return await get_all_by_user(db, user_id, Show)


async def update_show(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
    show_data: ShowUpdate,
) -> Show:
    """Update the show with the supplied fields."""
    return await update_media(db, show_id, user_id, Show, show_data)


async def delete_show(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a show."""
    await delete_media(db, show_id, user_id, Show)


# ===== Utility Functions =====


async def check_duplicate(
    db: AsyncSession,
    user_id: UUID,
    title: str
) -> dict[str, list[dict[str, str | None]]]:
    """Check for similar titles across all media types"""
    duplicates: dict[str, list[dict[str, str | None]]] = {
        "books": [],
        "games": [],
        "movies": [],
        "shows": []
    }

    for name, model in [("books", Book), ("games", Game), ("movies", Movie), ("shows", Show)]:
        result = await db.execute(
            select(model)
            .where(model.user_id == user_id)
            .where(model.title.ilike(f"%{title}%"))
        )
        matches = result.scalars().all()

        duplicates[name] = [
            {
                "id": str(m.id),
                "title": m.title,
                "status": m.status,
                "completed_at": m.completed_at.isoformat() if m.completed_at else None
            }
            for m in matches
        ]

    return duplicates


async def get_yearly_stats(
    db: AsyncSession,
    user_id: UUID,
    year: int
) -> dict[str, int]:
    """Get completion counts for all media types for a given year"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    stats: dict[str, int] = {}
    for name, model in [("books", Book), ("games", Game), ("movies", Movie), ("shows", Show)]:
        result = await db.execute(
            select(func.count(model.id))
            .where(model.user_id == user_id)
            .where(model.completed_at.between(start_date, end_date))
        )
        stats[name] = result.scalar() or 0

    return stats


async def search_media(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    media_type: str | None = None
) -> dict[str, list[Book | Game | Movie | Show]]:
    """Search across all media types by title"""
    results: dict[str, list[Book | Game | Movie | Show]] = {"books": [], "games": [], "movies": [], "shows": []}
    search_term = f"%{query}%"

    models_to_search: list[tuple[str, type[Book] | type[Game] | type[Movie] | type[Show]]] = []
    if media_type is None:
        models_to_search = [("books", Book), ("games", Game), ("movies", Movie), ("shows", Show)]
    elif media_type == "book":
        models_to_search = [("books", Book)]
    elif media_type == "game":
        models_to_search = [("games", Game)]
    elif media_type == "movie":
        models_to_search = [("movies", Movie)]
    elif media_type == "show":
        models_to_search = [("shows", Show)]

    for name, model in models_to_search:
        search_conditions = [model.title.ilike(search_term)]
        if hasattr(model, "notes"):
            search_conditions.append(model.notes.ilike(search_term))

        result = await db.execute(
            select(model)
            .where(model.user_id == user_id)
            .where(or_(*search_conditions))
            .limit(20)
        )
        results[name] = list(result.scalars().all())

    return results
