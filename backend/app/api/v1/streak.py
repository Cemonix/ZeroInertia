from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.streak import StreakResponse
from app.services import streak_service

router = APIRouter()


@router.get("/", response_model=StreakResponse, status_code=status.HTTP_200_OK)
async def get_streak(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreakResponse:
    """Get streak statistics for the authenticated user."""
    streak = await streak_service.get_or_create_user_streak(db, current_user.id)
    return StreakResponse.model_validate(streak)
