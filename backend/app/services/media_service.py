from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.exceptions import MediaNotFoundException
from app.models.media import Book, Game, Media, Movie, Show
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

# pyright: reportAny=false

# ===== Book Service Functions =====


async def create_book(
    db: AsyncSession,
    user_id: UUID,
    book_data: BookCreate,
) -> Book:
    """Create a new book for the given user."""
    new_book = Book(
        user_id=user_id,
        media_type="book",
        title=book_data.title,
        status=book_data.status.value,
        rating=book_data.rating,
        started_at=book_data.started_at,
        completed_at=book_data.completed_at,
        notes=book_data.notes,
        author=book_data.author,
        pages=book_data.pages,
        isbn=book_data.isbn,
        publisher=book_data.publisher,
    )
    db.add(new_book)
    await db.commit()
    await db.refresh(new_book)
    return new_book


async def get_book_by_id(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> Book | None:
    """Return a specific book for the user."""
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == user_id)
    )
    return result.scalars().first()


async def update_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    book_data: BookUpdate,
) -> Book:
    """Update the book with the supplied fields."""
    book = await get_book_by_id(db=db, book_id=book_id, user_id=user_id)
    if book is None:
        raise MediaNotFoundException(str(book_id))

    update_dict = book_data.model_dump(exclude_unset=True)

    # Convert enum to value if status is provided
    if "status" in update_dict and update_dict["status"] is not None:
        update_dict["status"] = update_dict["status"].value

    for field, value in update_dict.items():
        setattr(book, field, value)

    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a book."""
    book = await get_book_by_id(db=db, book_id=book_id, user_id=user_id)
    if book is None:
        raise MediaNotFoundException(str(book_id))

    await db.delete(book)
    await db.commit()


# ===== Movie Service Functions =====


async def create_movie(
    db: AsyncSession,
    user_id: UUID,
    movie_data: MovieCreate,
) -> Movie:
    """Create a new movie for the given user."""
    new_movie = Movie(
        user_id=user_id,
        media_type="movie",
        title=movie_data.title,
        status=movie_data.status.value,
        rating=movie_data.rating,
        started_at=movie_data.started_at,
        completed_at=movie_data.completed_at,
        notes=movie_data.notes,
        director=movie_data.director,
        duration_minutes=movie_data.duration_minutes,
        release_year=movie_data.release_year,
        genre=movie_data.genre,
    )
    db.add(new_movie)
    await db.commit()
    await db.refresh(new_movie)
    return new_movie


async def get_movie_by_id(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
) -> Movie | None:
    """Return a specific movie for the user."""
    result = await db.execute(
        select(Movie).where(Movie.id == movie_id, Movie.user_id == user_id)
    )
    return result.scalars().first()


async def update_movie(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
    movie_data: MovieUpdate,
) -> Movie:
    """Update the movie with the supplied fields."""
    movie = await get_movie_by_id(db=db, movie_id=movie_id, user_id=user_id)
    if movie is None:
        raise MediaNotFoundException(str(movie_id))

    update_dict = movie_data.model_dump(exclude_unset=True)

    if "status" in update_dict and update_dict["status"] is not None:
        update_dict["status"] = update_dict["status"].value

    for field, value in update_dict.items():
        setattr(movie, field, value)

    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


async def delete_movie(
    db: AsyncSession,
    movie_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a movie."""
    movie = await get_movie_by_id(db=db, movie_id=movie_id, user_id=user_id)
    if movie is None:
        raise MediaNotFoundException(str(movie_id))

    await db.delete(movie)
    await db.commit()


# ===== Game Service Functions =====


async def create_game(
    db: AsyncSession,
    user_id: UUID,
    game_data: GameCreate,
) -> Game:
    """Create a new game for the given user."""
    new_game = Game(
        user_id=user_id,
        media_type="game",
        title=game_data.title,
        status=game_data.status.value,
        rating=game_data.rating,
        started_at=game_data.started_at,
        completed_at=game_data.completed_at,
        notes=game_data.notes,
        platform=game_data.platform,
        developer=game_data.developer,
        playtime_hours=game_data.playtime_hours,
        genre=game_data.genre,
        is_100_percent=game_data.is_100_percent,
    )
    db.add(new_game)
    await db.commit()
    await db.refresh(new_game)
    return new_game


async def get_game_by_id(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> Game | None:
    """Return a specific game for the user."""
    result = await db.execute(
        select(Game).where(Game.id == game_id, Game.user_id == user_id)
    )
    return result.scalars().first()


async def update_game(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
    game_data: GameUpdate,
) -> Game:
    """Update the game with the supplied fields."""
    game = await get_game_by_id(db=db, game_id=game_id, user_id=user_id)
    if game is None:
        raise MediaNotFoundException(str(game_id))

    update_dict = game_data.model_dump(exclude_unset=True)

    if "status" in update_dict and update_dict["status"] is not None:
        update_dict["status"] = update_dict["status"].value

    for field, value in update_dict.items():
        setattr(game, field, value)

    db.add(game)
    await db.commit()
    await db.refresh(game)
    return game


async def delete_game(
    db: AsyncSession,
    game_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a game."""
    game = await get_game_by_id(db=db, game_id=game_id, user_id=user_id)
    if game is None:
        raise MediaNotFoundException(str(game_id))

    await db.delete(game)
    await db.commit()


# ===== Show Service Functions =====


async def create_show(
    db: AsyncSession,
    user_id: UUID,
    show_data: ShowCreate,
) -> Show:
    """Create a new TV show season for the given user."""
    new_show = Show(
        user_id=user_id,
        media_type="show",
        title=show_data.title,
        status=show_data.status.value,
        rating=show_data.rating,
        started_at=show_data.started_at,
        completed_at=show_data.completed_at,
        notes=show_data.notes,
        season_number=show_data.season_number,
        episodes=show_data.episodes,
        creator=show_data.creator,
        release_year=show_data.release_year,
        genre=show_data.genre,
    )
    db.add(new_show)
    await db.commit()
    await db.refresh(new_show)
    return new_show


async def get_show_by_id(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
) -> Show | None:
    """Return a specific show for the user."""
    result = await db.execute(
        select(Show).where(Show.id == show_id, Show.user_id == user_id)
    )
    return result.scalars().first()


async def update_show(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
    show_data: ShowUpdate,
) -> Show:
    """Update the show with the supplied fields."""
    show = await get_show_by_id(db=db, show_id=show_id, user_id=user_id)
    if show is None:
        raise MediaNotFoundException(str(show_id))

    update_dict = show_data.model_dump(exclude_unset=True)

    if "status" in update_dict and update_dict["status"] is not None:
        update_dict["status"] = update_dict["status"].value

    for field, value in update_dict.items():
        setattr(show, field, value)

    db.add(show)
    await db.commit()
    await db.refresh(show)
    return show


async def delete_show(
    db: AsyncSession,
    show_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a show."""
    show = await get_show_by_id(db=db, show_id=show_id, user_id=user_id)
    if show is None:
        raise MediaNotFoundException(str(show_id))

    await db.delete(show)
    await db.commit()


# ===== General Media Functions =====


async def get_all_media(
    db: AsyncSession,
    user_id: UUID,
    media_type: str | None = None,
    status: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    search: str | None = None,
) -> Sequence[Media]:
    """Return all media items for the user with optional filters."""
    query = select(Media).where(Media.user_id == user_id)

    if media_type:
        query = query.where(Media.media_type == media_type)
    if status:
        query = query.where(Media.status == status)

    # Rating filters
    if rating_min is not None:
        query = query.where(Media.rating >= rating_min)
    if rating_max is not None:
        query = query.where(Media.rating <= rating_max)

    # Search in title and notes (case-insensitive)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (Media.title.ilike(search_term)) | (Media.notes.ilike(search_term))
        )

    # Order by created_at descending (newest first)
    query = query.order_by(Media.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()
