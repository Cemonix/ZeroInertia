from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.core.logging import logger
from app.models.user import User
from app.schemas.priority import PriorityResponse
from app.services import priority_service

router = APIRouter()


@router.get("/", response_model=list[PriorityResponse])
async def get_priorities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PriorityResponse]:
    """Get all available priorities."""
    logger.info(f"User {current_user.id} fetching priorities")
    priorities = await priority_service.get_all_priorities(db)
    return [PriorityResponse.model_validate(priority) for priority in priorities]
