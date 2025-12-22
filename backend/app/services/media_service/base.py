from collections.abc import Sequence
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import MediaNotFoundException
from app.models.media import Anime, Book, Game, Manga, Movie, Show

MediaModel = TypeVar("MediaModel", Anime, Book, Game, Manga, Movie, Show)

# pyright: reportAny=false


async def get_all_by_user(
    db: AsyncSession,
    user_id: UUID,
    model: type[MediaModel],
) -> Sequence[MediaModel]:
    """Get all media of a specific type for a user"""
    result = await db.execute(
        select(model)
        .options(selectinload(model.genres))
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
        select(model)
        .options(selectinload(model.genres))
        .where(model.id == media_id, model.user_id == user_id)
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
        .options(selectinload(model.genres))
        .where(model.user_id == user_id, model.status == status)
        .order_by(model.created_at.desc())
    )
    return result.scalars().all()


async def reload_media_with_genres(
    db: AsyncSession,
    media_id: UUID,
    user_id: UUID,
    model: type[MediaModel],
) -> MediaModel:
    """Reload a media item with its genres eagerly loaded"""
    media = await get_by_id(db, media_id, user_id, model)
    if media is None:
        raise MediaNotFoundException(str(media_id))
    return media


async def create_media(
    db: AsyncSession,
    model: type[MediaModel],
    data: dict[str, object],
) -> MediaModel:
    """Generic create for any media type"""
    media_item = model(**data)
    db.add(media_item)
    await db.commit()
    return await reload_media_with_genres(db, media_item.id, media_item.user_id, model)


async def update_media(
    db: AsyncSession,
    media_id: UUID,
    user_id: UUID,
    model: type[MediaModel],
    update_schema: BaseModel,
) -> MediaModel:
    """Generic update for any media type"""
    from app.services.base_service import apply_updates_async

    media = await get_by_id(db, media_id, user_id, model)
    if media is None:
        raise MediaNotFoundException(str(media_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                media.status = value
            else:
                media.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    _ = await apply_updates_async(
        model=media,
        update_schema=update_schema,
        custom_handlers={"status": handle_status}
    )

    db.add(media)
    await db.commit()
    return await reload_media_with_genres(db, media.id, user_id, model)


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
