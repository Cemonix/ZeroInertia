from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import GenreNotFoundException
from app.models.user import User
from app.schemas.media import GenreCreate, GenreResponse, GenreUpdate
from app.services import genre_service

router = APIRouter()


@router.get("/genres", response_model=list[GenreResponse])
async def list_genres(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[GenreResponse]:
    """Return all genres for the authenticated user."""
    genres = await genre_service.get_all_genres(db=db, user_id=current_user.id)
    return [GenreResponse.model_validate(genre) for genre in genres]


@router.post("/genres", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(
    genre_data: GenreCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenreResponse:
    """Create a new genre for the authenticated user."""
    genre = await genre_service.create_genre(
        db=db,
        user_id=current_user.id,
        genre_data=genre_data,
    )
    return GenreResponse.model_validate(genre)


@router.get("/genres/{genre_id}", response_model=GenreResponse)
async def get_genre(
    genre_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenreResponse:
    """Return a single genre for the authenticated user."""
    genre = await genre_service.get_genre_by_id(db=db, genre_id=genre_id, user_id=current_user.id)
    if not genre:
        raise GenreNotFoundException(str(genre_id))
    return GenreResponse.model_validate(genre)


@router.patch("/genres/{genre_id}", response_model=GenreResponse)
async def update_genre(
    genre_id: UUID,
    genre_data: GenreUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenreResponse:
    """Update a genre for the authenticated user."""
    genre = await genre_service.update_genre(
        db=db,
        genre_id=genre_id,
        user_id=current_user.id,
        genre_data=genre_data,
    )
    return GenreResponse.model_validate(genre)


@router.delete("/genres/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(
    genre_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a genre for the authenticated user."""
    await genre_service.delete_genre(db=db, genre_id=genre_id, user_id=current_user.id)
