from uuid import UUID

from fastapi import Depends, Query, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.api.v1.pagination_deps import get_pagination_params
from app.core.database import get_db
from app.core.exceptions import MediaNotFoundException
from app.models.user import User
from app.schemas.media import (
    BookCreate,
    BookResponse,
    BookUpdate,
    GameCreate,
    GameResponse,
    GameUpdate,
    MovieCreate,
    MovieResponse,
    MovieUpdate,
    ShowCreate,
    ShowResponse,
    ShowUpdate,
)
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services import media_service

router = APIRouter()


# ===== Book Endpoints =====


@router.get("/books", response_model=PaginatedResponse[BookResponse])
async def list_books(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    rating_min: int | None = Query(None, ge=0, le=100),
    rating_max: int | None = Query(None, ge=0, le=100),
    search: str | None = Query(None, min_length=1),
) -> PaginatedResponse[BookResponse]:
    """Return books for the authenticated user with pagination."""
    media_items, total = await media_service.get_all_media(
        db=db,
        user_id=current_user.id,
        media_type="book",
        status=status_filter,
        rating_min=rating_min,
        rating_max=rating_max,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    book_responses = [BookResponse.model_validate(item) for item in media_items]
    return PaginatedResponse[BookResponse].create(
        items=book_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


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


@router.get("/movies", response_model=PaginatedResponse[MovieResponse])
async def list_movies(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    rating_min: int | None = Query(None, ge=0, le=100),
    rating_max: int | None = Query(None, ge=0, le=100),
    search: str | None = Query(None, min_length=1),
) -> PaginatedResponse[MovieResponse]:
    """Return movies for the authenticated user with pagination."""
    media_items, total = await media_service.get_all_media(
        db=db,
        user_id=current_user.id,
        media_type="movie",
        status=status_filter,
        rating_min=rating_min,
        rating_max=rating_max,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    movie_responses = [MovieResponse.model_validate(item) for item in media_items]
    return PaginatedResponse[MovieResponse].create(
        items=movie_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


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


@router.get("/games", response_model=PaginatedResponse[GameResponse])
async def list_games(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    rating_min: int | None = Query(None, ge=0, le=100),
    rating_max: int | None = Query(None, ge=0, le=100),
    search: str | None = Query(None, min_length=1),
) -> PaginatedResponse[GameResponse]:
    """Return games for the authenticated user with pagination."""
    media_items, total = await media_service.get_all_media(
        db=db,
        user_id=current_user.id,
        media_type="game",
        status=status_filter,
        rating_min=rating_min,
        rating_max=rating_max,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    game_responses = [GameResponse.model_validate(item) for item in media_items]
    return PaginatedResponse[GameResponse].create(
        items=game_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


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


@router.get("/shows", response_model=PaginatedResponse[ShowResponse])
async def list_shows(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status_filter: str | None = Query(None, alias="status"),
    rating_min: int | None = Query(None, ge=0, le=100),
    rating_max: int | None = Query(None, ge=0, le=100),
    search: str | None = Query(None, min_length=1),
) -> PaginatedResponse[ShowResponse]:
    """Return TV shows for the authenticated user with pagination."""
    media_items, total = await media_service.get_all_media(
        db=db,
        user_id=current_user.id,
        media_type="show",
        status=status_filter,
        rating_min=rating_min,
        rating_max=rating_max,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    show_responses = [ShowResponse.model_validate(item) for item in media_items]
    return PaginatedResponse[ShowResponse].create(
        items=show_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


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


# ===== General Media Endpoints =====


@router.get("/", response_model=PaginatedResponse[BookResponse | MovieResponse | GameResponse | ShowResponse])
async def list_all_media(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    media_type: str | None = Query(None, alias="type"),
    status_filter: str | None = Query(None, alias="status"),
    rating_min: int | None = Query(None, ge=0, le=100, description="Minimum rating (0-100)"),
    rating_max: int | None = Query(None, ge=0, le=100, description="Maximum rating (0-100)"),
    search: str | None = Query(None, min_length=1, description="Search in title and notes"),
) -> PaginatedResponse[BookResponse | MovieResponse | GameResponse | ShowResponse]:
    """Return media items for the authenticated user with optional filters and pagination."""
    media_items, total = await media_service.get_all_media(
        db=db,
        user_id=current_user.id,
        media_type=media_type,
        status=status_filter,
        rating_min=rating_min,
        rating_max=rating_max,
        search=search,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    # Convert to appropriate response models based on media_type
    responses: list[BookResponse | MovieResponse | GameResponse | ShowResponse] = []
    for item in media_items:
        if item.media_type == "book":
            responses.append(BookResponse.model_validate(item))
        elif item.media_type == "movie":
            responses.append(MovieResponse.model_validate(item))
        elif item.media_type == "game":
            responses.append(GameResponse.model_validate(item))
        elif item.media_type == "show":
            responses.append(ShowResponse.model_validate(item))

    return PaginatedResponse[BookResponse | MovieResponse | GameResponse | ShowResponse].create(
        items=responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )
