from datetime import datetime
from uuid import UUID

from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import MediaNotFoundException
from app.models.user import User
from app.schemas.media import (
    BookCreate,
    BookResponse,
    BookUpdate,
    DuplicateCheckResponse,
    GameCreate,
    GameResponse,
    GameUpdate,
    MovieCreate,
    MovieResponse,
    MovieUpdate,
    ShowCreate,
    ShowResponse,
    ShowUpdate,
    YearlyStatsResponse,
)
from app.services import media_service

router = APIRouter()


# ===== Book Endpoints =====


@router.get("/books", response_model=list[BookResponse])
async def list_books(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
) -> list[BookResponse]:
    """Return all books for the authenticated user."""
    if status_filter:
        books = await media_service.get_by_status(
            db=db,
            user_id=current_user.id,
            model=media_service.Book,
            status=status_filter,
        )
    else:
        books = await media_service.get_all_books(db=db, user_id=current_user.id)

    return [BookResponse.model_validate(book) for book in books]


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    """Create a new book for the authenticated user."""
    book = await media_service.create_book(
        db=db,
        user_id=current_user.id,
        book_data=book_data,
    )
    return BookResponse.model_validate(book)


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    """Return a single book for the authenticated user."""
    book = await media_service.get_book_by_id(db=db, book_id=book_id, user_id=current_user.id)
    if not book:
        raise MediaNotFoundException(str(book_id))
    return BookResponse.model_validate(book)


@router.patch("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BookResponse:
    """Update a book for the authenticated user."""
    book = await media_service.update_book(
        db=db,
        book_id=book_id,
        user_id=current_user.id,
        book_data=book_data,
    )
    return BookResponse.model_validate(book)


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a book for the authenticated user."""
    await media_service.delete_book(db=db, book_id=book_id, user_id=current_user.id)


# ===== Movie Endpoints =====


@router.get("/movies", response_model=list[MovieResponse])
async def list_movies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
) -> list[MovieResponse]:
    """Return all movies for the authenticated user."""
    if status_filter:
        movies = await media_service.get_by_status(
            db=db,
            user_id=current_user.id,
            model=media_service.Movie,
            status=status_filter,
        )
    else:
        movies = await media_service.get_all_movies(db=db, user_id=current_user.id)

    return [MovieResponse.model_validate(movie) for movie in movies]


@router.post("/movies", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MovieResponse:
    """Create a new movie for the authenticated user."""
    movie = await media_service.create_movie(
        db=db,
        user_id=current_user.id,
        movie_data=movie_data,
    )
    return MovieResponse.model_validate(movie)


@router.get("/movies/{movie_id}", response_model=MovieResponse)
async def get_movie(
    movie_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MovieResponse:
    """Return a single movie for the authenticated user."""
    movie = await media_service.get_movie_by_id(db=db, movie_id=movie_id, user_id=current_user.id)
    if not movie:
        raise MediaNotFoundException(str(movie_id))
    return MovieResponse.model_validate(movie)


@router.patch("/movies/{movie_id}", response_model=MovieResponse)
async def update_movie(
    movie_id: UUID,
    movie_data: MovieUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MovieResponse:
    """Update a movie for the authenticated user."""
    movie = await media_service.update_movie(
        db=db,
        movie_id=movie_id,
        user_id=current_user.id,
        movie_data=movie_data,
    )
    return MovieResponse.model_validate(movie)


@router.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a movie for the authenticated user."""
    await media_service.delete_movie(db=db, movie_id=movie_id, user_id=current_user.id)


# ===== Game Endpoints =====


@router.get("/games", response_model=list[GameResponse])
async def list_games(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
) -> list[GameResponse]:
    """Return all games for the authenticated user."""
    if status_filter:
        games = await media_service.get_by_status(
            db=db,
            user_id=current_user.id,
            model=media_service.Game,
            status=status_filter,
        )
    else:
        games = await media_service.get_all_games(db=db, user_id=current_user.id)

    return [GameResponse.model_validate(game) for game in games]


@router.post("/games", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
async def create_game(
    game_data: GameCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    """Create a new game for the authenticated user."""
    game = await media_service.create_game(
        db=db,
        user_id=current_user.id,
        game_data=game_data,
    )
    return GameResponse.model_validate(game)


@router.get("/games/{game_id}", response_model=GameResponse)
async def get_game(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    """Return a single game for the authenticated user."""
    game = await media_service.get_game_by_id(db=db, game_id=game_id, user_id=current_user.id)
    if not game:
        raise MediaNotFoundException(str(game_id))
    return GameResponse.model_validate(game)


@router.patch("/games/{game_id}", response_model=GameResponse)
async def update_game(
    game_id: UUID,
    game_data: GameUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GameResponse:
    """Update a game for the authenticated user."""
    game = await media_service.update_game(
        db=db,
        game_id=game_id,
        user_id=current_user.id,
        game_data=game_data,
    )
    return GameResponse.model_validate(game)


@router.delete("/games/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a game for the authenticated user."""
    await media_service.delete_game(db=db, game_id=game_id, user_id=current_user.id)


# ===== Show Endpoints =====


@router.get("/shows", response_model=list[ShowResponse])
async def list_shows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
) -> list[ShowResponse]:
    """Return all TV shows for the authenticated user."""
    if status_filter:
        shows = await media_service.get_by_status(
            db=db,
            user_id=current_user.id,
            model=media_service.Show,
            status=status_filter,
        )
    else:
        shows = await media_service.get_all_shows(db=db, user_id=current_user.id)

    return [ShowResponse.model_validate(show) for show in shows]


@router.post("/shows", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
async def create_show(
    show_data: ShowCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShowResponse:
    """Create a new TV show season for the authenticated user."""
    show = await media_service.create_show(
        db=db,
        user_id=current_user.id,
        show_data=show_data,
    )
    return ShowResponse.model_validate(show)


@router.get("/shows/{show_id}", response_model=ShowResponse)
async def get_show(
    show_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShowResponse:
    """Return a single TV show for the authenticated user."""
    show = await media_service.get_show_by_id(db=db, show_id=show_id, user_id=current_user.id)
    if not show:
        raise MediaNotFoundException(str(show_id))
    return ShowResponse.model_validate(show)


@router.patch("/shows/{show_id}", response_model=ShowResponse)
async def update_show(
    show_id: UUID,
    show_data: ShowUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShowResponse:
    """Update a TV show for the authenticated user."""
    show = await media_service.update_show(
        db=db,
        show_id=show_id,
        user_id=current_user.id,
        show_data=show_data,
    )
    return ShowResponse.model_validate(show)


@router.delete("/shows/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_show(
    show_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a TV show for the authenticated user."""
    await media_service.delete_show(db=db, show_id=show_id, user_id=current_user.id)


# ===== Utility Endpoints =====


@router.get("/duplicate-check", response_model=DuplicateCheckResponse)
async def check_duplicate_title(
    title: str = Query(..., min_length=1, description="Title to search for duplicates"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DuplicateCheckResponse:
    """Check for similar titles across all media types."""
    duplicates = await media_service.check_duplicate(
        db=db,
        user_id=current_user.id,
        title=title,
    )
    return DuplicateCheckResponse(**duplicates)


@router.get("/stats/yearly", response_model=YearlyStatsResponse)
async def get_yearly_stats(
    year: int | None = Query(None, description="Year to get stats for (defaults to current year)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> YearlyStatsResponse:
    """Get completion counts for all media types for a given year."""
    if year is None:
        year = datetime.now().year

    stats = await media_service.get_yearly_stats(
        db=db,
        user_id=current_user.id,
        year=year,
    )
    return YearlyStatsResponse(year=year, **stats)
