from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import GenreNotFoundException
from app.models.genre import Genre
from app.schemas.media import GenreCreate, GenreUpdate


async def get_all_genres(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Genre]:
    """Get all genres for a user"""
    result = await db.execute(
        select(Genre)
        .where(Genre.user_id == user_id)
        .order_by(Genre.name)
    )
    return result.scalars().all()


async def get_genre_by_id(
    db: AsyncSession,
    genre_id: UUID,
    user_id: UUID,
) -> Genre | None:
    """Get a specific genre by ID"""
    result = await db.execute(
        select(Genre).where(Genre.id == genre_id, Genre.user_id == user_id)
    )
    return result.scalars().first()


async def get_or_create_genre(
    db: AsyncSession,
    user_id: UUID,
    name: str,
) -> Genre:
    """Get existing genre by name or create new one"""
    result = await db.execute(
        select(Genre).where(Genre.user_id == user_id, Genre.name == name)
    )
    genre = result.scalars().first()

    if genre:
        return genre

    new_genre = Genre(user_id=user_id, name=name)
    db.add(new_genre)
    await db.flush()
    return new_genre


async def create_genre(
    db: AsyncSession,
    user_id: UUID,
    genre_data: GenreCreate,
) -> Genre:
    """Create a new genre for the user"""
    genre = Genre(
        user_id=user_id,
        name=genre_data.name,
    )
    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


async def update_genre(
    db: AsyncSession,
    genre_id: UUID,
    user_id: UUID,
    genre_data: GenreUpdate,
) -> Genre:
    """Update a genre"""
    genre = await get_genre_by_id(db, genre_id, user_id)
    if genre is None:
        raise GenreNotFoundException(str(genre_id))

    genre.name = genre_data.name

    db.add(genre)
    await db.commit()
    await db.refresh(genre)
    return genre


async def delete_genre(
    db: AsyncSession,
    genre_id: UUID,
    user_id: UUID,
) -> None:
    """Delete a genre"""
    genre = await get_genre_by_id(db, genre_id, user_id)
    if genre is None:
        raise GenreNotFoundException(str(genre_id))

    await db.delete(genre)
    await db.commit()


async def get_genres_by_ids(
    db: AsyncSession,
    user_id: UUID,
    genre_ids: list[UUID],
) -> Sequence[Genre]:
    """Get multiple genres by their IDs"""
    result = await db.execute(
        select(Genre)
        .where(Genre.user_id == user_id, Genre.id.in_(genre_ids))
    )
    return result.scalars().all()
