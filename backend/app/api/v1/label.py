from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import LabelNotFoundException
from app.models.user import User
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services import label_service

router = APIRouter()


@router.post("/", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(
    label_data: LabelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """Create a new label for the authenticated user."""
    new_label = await label_service.create_label(
        db=db,
        user_id=current_user.id,
        name=label_data.name,
        color=label_data.color,
        description=label_data.description,
        order_index=label_data.order_index,
    )

    return LabelResponse.model_validate(new_label)


@router.get("/", response_model=list[LabelResponse])
async def get_labels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[LabelResponse]:
    """Get all labels for the authenticated user."""
    labels = await label_service.get_labels(db=db, user_id=current_user.id)
    return [LabelResponse.model_validate(label) for label in labels]


@router.get("/{label_id}", response_model=LabelResponse)
async def get_label(
    label_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """Get a specific label."""
    label = await label_service.get_label_by_id(db=db, label_id=label_id, user_id=current_user.id)
    if label is None:
        raise LabelNotFoundException(str(label_id))
    return LabelResponse.model_validate(label)


@router.patch("/{label_id}", response_model=LabelResponse)
async def update_label(
    label_id: UUID,
    label_data: LabelUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LabelResponse:
    """Update a label."""
    updated_label = await label_service.update_label(
        db=db,
        label_id=label_id,
        user_id=current_user.id,
        update_data=label_data,
    )

    return LabelResponse.model_validate(updated_label)


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    label_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a label."""
    await label_service.delete_label(db=db, label_id=label_id, user_id=current_user.id)
