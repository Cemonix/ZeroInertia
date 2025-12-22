from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Movie
from app.schemas.media import CSVImportResult, MovieCreate, MovieUpdate
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

async def create_movie(
    db: AsyncSession,
    user_id: UUID,
    movie_data: MovieCreate,
) -> Movie:
    """Create a new movie for the given user."""
    data = movie_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    movie = Movie(**data)

    if movie_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, movie_data.genre_ids)
        movie.genres = list(genres)

    db.add(movie)
    await db.commit()
    return await reload_media_with_genres(db, movie.id, user_id, Movie)


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
    movie = await get_by_id(db, movie_id, user_id, Movie)
    if movie is None:
        raise MediaNotFoundException(str(movie_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                movie.status = value
            else:
                movie.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            movie.genres = list(genres)

    _ = await apply_updates_async(
        model=movie,
        update_schema=movie_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(movie)
    await db.commit()
    return await reload_media_with_genres(db, movie.id, user_id, Movie)


async def delete_movie(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a movie."""
    await delete_media(db, movie_id, user_id, Movie)


async def import_movies_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import movies from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Movie,
        create_schema=MovieCreate,
    )
