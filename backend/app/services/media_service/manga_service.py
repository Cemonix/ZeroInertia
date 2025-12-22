from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Manga
from app.schemas.media import CSVImportResult, MangaCreate, MangaUpdate
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

async def create_manga(
    db: AsyncSession,
    user_id: UUID,
    manga_data: MangaCreate,
) -> Manga:
    """Create a new manga for the given user."""
    data = manga_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    manga = Manga(**data)

    if manga_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, manga_data.genre_ids)
        manga.genres = list(genres)

    db.add(manga)
    await db.commit()
    return await reload_media_with_genres(db, manga.id, user_id, Manga)


async def get_manga_by_id(
    db: AsyncSession,
    manga_id: UUID,
    user_id: UUID,
) -> Manga | None:
    """Return a specific manga for the user."""
    return await get_by_id(db, manga_id, user_id, Manga)


async def get_all_manga(
    db: AsyncSession,
    user_id: UUID,
) -> Sequence[Manga]:
    """Return all manga for the user."""
    return await get_all_by_user(db, user_id, Manga)


async def update_manga(
    db: AsyncSession,
    manga_id: UUID,
    user_id: UUID,
    manga_data: MangaUpdate,
) -> Manga:
    """Update the manga with the supplied fields."""
    manga = await get_by_id(db, manga_id, user_id, Manga)
    if manga is None:
        raise MediaNotFoundException(str(manga_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                manga.status = value
            else:
                manga.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            manga.genres = list(genres)

    _ = await apply_updates_async(
        model=manga,
        update_schema=manga_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(manga)
    await db.commit()
    return await reload_media_with_genres(db, manga.id, user_id, Manga)


async def delete_manga(
    db: AsyncSession,
    manga_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a manga."""
    await delete_media(db, manga_id, user_id, Manga)


async def import_manga_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import manga from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Manga,
        create_schema=MangaCreate,
    )
