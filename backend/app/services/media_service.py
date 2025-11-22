from collections.abc import Sequence
from datetime import date
from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import MediaNotFoundException
from app.models.media import Anime, Book, Game, Manga, Movie, Show
from app.schemas.media import (
    AnimeCreate,
    AnimeUpdate,
    BookCreate,
    BookUpdate,
    GameCreate,
    GameUpdate,
    MangaCreate,
    MangaUpdate,
    MovieCreate,
    MovieUpdate,
    ShowCreate,
    ShowUpdate,
)
from app.services.base_service import apply_updates_async
from app.services.genre_service import get_genres_by_ids

MediaModel = TypeVar("MediaModel", Anime, Book, Game, Manga, Movie, Show)

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


# ===== Book Service Functions =====


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


# ===== Movie Service Functions =====


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


# ===== Game Service Functions =====


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


# ===== Show Service Functions =====


async def create_show(
    db: AsyncSession,
    user_id: UUID,
    show_data: ShowCreate,
) -> Show:
    """Create a new TV show season for the given user."""
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


# ===== Manga Service Functions =====


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


# ===== Anime Service Functions =====


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


# ===== Utility Functions =====


async def check_duplicate(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    media_type: str
) -> list[dict[str, str | None]]:
    """Check for similar titles within a specific media type"""
    media_type_map = {
        "book": Book,
        "game": Game,
        "movie": Movie,
        "show": Show,
        "manga": Manga,
        "anime": Anime
    }

    model = media_type_map.get(media_type)
    if not model:
        raise ValueError(f"Invalid media type: {media_type}")

    result = await db.execute(
        select(model)
        .where(model.user_id == user_id)
        .where(model.title.ilike(f"%{title}%"))
    )
    matches = result.scalars().all()

    return [
        {
            "id": str(m.id),
            "title": m.title,
            "status": m.status,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None
        }
        for m in matches
    ]


async def get_yearly_stats(
    db: AsyncSession,
    user_id: UUID,
    year: int
) -> dict[str, int]:
    """Get completion counts for all media types for a given year"""
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    stats: dict[str, int] = {}
    for name, model in [("books", Book), ("games", Game), ("manga", Manga), ("anime", Anime), ("movies", Movie), ("shows", Show)]:
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
) -> dict[str, list[Book | Game | Manga | Anime | Movie | Show]]:
    """Search across all media types by title"""
    results: dict[str, list[Book | Game | Manga | Anime | Movie | Show]] = {"books": [], "games": [], "manga": [], "anime": [], "movies": [], "shows": []}
    search_term = f"%{query}%"

    models_to_search: list[tuple[str, type[Book] | type[Game] | type[Manga] | type[Anime] | type[Movie] | type[Show]]] = []
    if media_type is None:
        models_to_search = [("books", Book), ("games", Game), ("manga", Manga), ("anime", Anime), ("movies", Movie), ("shows", Show)]
    elif media_type == "book":
        models_to_search = [("books", Book)]
    elif media_type == "game":
        models_to_search = [("games", Game)]
    elif media_type == "manga":
        models_to_search = [("manga", Manga)]
    elif media_type == "anime":
        models_to_search = [("anime", Anime)]
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
