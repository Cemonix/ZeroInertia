from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Show
from app.schemas.media import CSVImportResult, ShowCreate, ShowUpdate
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

async def create_show(
    db: AsyncSession,
    user_id: UUID,
    show_data: ShowCreate,
) -> Show:
    """Create a new TV show for the given user."""
    data = show_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    show = Show(**data)

    if show_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, show_data.genre_ids)
        show.genres = list(genres)

    db.add(show)
    await db.commit()
    return await reload_media_with_genres(db, show.id, user_id, Show)


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
    show = await get_by_id(db, show_id, user_id, Show)
    if show is None:
        raise MediaNotFoundException(str(show_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                show.status = value
            else:
                show.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            show.genres = list(genres)

    _ = await apply_updates_async(
        model=show,
        update_schema=show_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(show)
    await db.commit()
    return await reload_media_with_genres(db, show.id, user_id, Show)


async def delete_show(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a show."""
    await delete_media(db, show_id, user_id, Show)


async def import_shows_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import TV shows from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Show,
        create_schema=ShowCreate,
    )
