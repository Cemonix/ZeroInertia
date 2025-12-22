from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Anime
from app.schemas.media import AnimeCreate, AnimeUpdate, CSVImportResult
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

async def create_anime(
    db: AsyncSession,
    user_id: UUID,
    anime_data: AnimeCreate,
) -> Anime:
    """Create a new anime for the given user."""
    data = anime_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    anime = Anime(**data)

    if anime_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, anime_data.genre_ids)
        anime.genres = list(genres)

    db.add(anime)
    await db.commit()
    return await reload_media_with_genres(db, anime.id, user_id, Anime)


async def get_anime_by_id(
    db: AsyncSession,
    anime_id: UUID,
    user_id: UUID,
) -> Anime | None:
    """Return a specific anime for the user."""
    return await get_by_id(db, anime_id, user_id, Anime)


async def get_all_anime(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Anime]:
    """Return all anime for the user."""
    return await get_all_by_user(db, user_id, Anime)


async def update_anime(
    db: AsyncSession,
    anime_id: UUID,
    user_id: UUID,
    anime_data: AnimeUpdate,
) -> Anime:
    """Update the anime with the supplied fields."""
    anime = await get_by_id(db, anime_id, user_id, Anime)
    if anime is None:
        raise MediaNotFoundException(str(anime_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                anime.status = value
            else:
                anime.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            anime.genres = list(genres)

    _ = await apply_updates_async(
        model=anime,
        update_schema=anime_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(anime)
    await db.commit()
    return await reload_media_with_genres(db, anime.id, user_id, Anime)


async def delete_anime(
    db: AsyncSession,
    anime_id: UUID,
    user_id: UUID,
) -> None:
    """Remove an anime."""
    await delete_media(db, anime_id, user_id, Anime)


async def import_anime_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import anime from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Anime,
        create_schema=AnimeCreate,
    )
