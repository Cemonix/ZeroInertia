from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import MediaNotFoundException
from app.models.media import Game
from app.schemas.media import CSVImportResult, GameCreate, GameUpdate
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

async def create_game(
    db: AsyncSession,
    user_id: UUID,
    game_data: GameCreate,
) -> Game:
    """Create a new game for the given user."""
    data = game_data.model_dump(exclude={"genre_ids"})
    data["user_id"] = user_id
    if "status" in data and hasattr(data["status"], "value"):
        data["status"] = data["status"].value

    game = Game(**data)

    if game_data.genre_ids:
        genres = await get_genres_by_ids(db, user_id, game_data.genre_ids)
        game.genres = list(genres)

    db.add(game)
    await db.commit()
    return await reload_media_with_genres(db, game.id, user_id, Game)


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
    game = await get_by_id(db, game_id, user_id, Game)
    if game is None:
        raise MediaNotFoundException(str(game_id))

    async def handle_status(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None:
            if isinstance(value, str):
                game.status = value
            else:
                game.status = str(value.value) if hasattr(value, "value") else str(value)  # pyright: ignore[reportAttributeAccessIssue]

    async def handle_genre_ids(_model: object, value: object, _updates: dict[str, object]) -> None:
        if value is not None and isinstance(value, list):
            genres = await get_genres_by_ids(db, user_id, value)
            game.genres = list(genres)

    _ = await apply_updates_async(
        model=game,
        update_schema=game_data,
        custom_handlers={"status": handle_status, "genre_ids": handle_genre_ids}
    )

    db.add(game)
    await db.commit()
    return await reload_media_with_genres(db, game.id, user_id, Game)


async def delete_game(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a game."""
    await delete_media(db, game_id, user_id, Game)


async def import_games_csv(
    db: AsyncSession,
    user_id: UUID,
    csv_content: str,
) -> CSVImportResult:
    """Import games from CSV file"""
    return await import_csv_generic(
        db=db,
        user_id=user_id,
        csv_content=csv_content,
        model=Game,
        create_schema=GameCreate,
    )
