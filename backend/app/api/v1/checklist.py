from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.checklist import (
    CheckListCreate,
    CheckListItemCreate,
    CheckListItemReorder,
    CheckListItemResponse,
    CheckListItemUpdate,
    CheckListReorder,
    CheckListResponse,
    CheckListUpdate,
)
from app.services import checklist_service, task_service

router = APIRouter()


# ==============================================================================
# CheckList Endpoints
# ==============================================================================


@router.post("/", response_model=CheckListResponse, status_code=status.HTTP_201_CREATED)
async def create_checklist(
    checklist_data: CheckListCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckListResponse:
    """Create a new checklist for a task."""
    # Verify that the task belongs to the current user
    task = await task_service.get_task_by_id(db=db, task_id=checklist_data.task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    new_checklist = await checklist_service.create_checklist(
        db=db, task_id=checklist_data.task_id, title=checklist_data.title
    )
    return CheckListResponse.model_validate(new_checklist)


@router.get("/", response_model=list[CheckListResponse])
async def get_checklists(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CheckListResponse]:
    """Get all checklists for a specific task."""
    # Verify that the task belongs to the current user
    task = await task_service.get_task_by_id(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    checklists = await checklist_service.get_checklists_by_task(db=db, task_id=task_id)
    return [CheckListResponse.model_validate(checklist) for checklist in checklists]


@router.get("/{checklist_id}", response_model=CheckListResponse)
async def get_checklist(
    checklist_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckListResponse:
    """Get a specific checklist by ID."""
    # Verify ownership before fetching
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    checklist = await checklist_service.get_checklist_by_id(db=db, checklist_id=checklist_id)
    if not checklist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    return CheckListResponse.model_validate(checklist)


@router.patch("/{checklist_id}", response_model=CheckListResponse)
async def update_checklist(
    checklist_id: UUID,
    checklist_data: CheckListUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckListResponse:
    """Update a checklist."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    try:
        updated_checklist = await checklist_service.update_checklist(
            db=db,
            checklist_id=checklist_id,
            title=checklist_data.title,
            order_index=checklist_data.order_index,
        )
        return CheckListResponse.model_validate(updated_checklist)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found") from None


@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist(
    checklist_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a checklist."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    try:
        await checklist_service.delete_checklist(db=db, checklist_id=checklist_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found") from None


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_checklists(
    reorder_data: list[CheckListReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reorder checklists."""
    # Verify ownership of all checklists
    for item in reorder_data:
        if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=item.id, user_id=current_user.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more checklists not found")

    reorder_list = [{"id": item.id, "order_index": item.order_index} for item in reorder_data]
    await checklist_service.reorder_checklists(db=db, reorder_data=reorder_list)


# ==============================================================================
# CheckListItem Endpoints
# ==============================================================================


@router.post(
    "/{checklist_id}/items",
    response_model=CheckListItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checklist_item(
    checklist_id: UUID,
    item_data: CheckListItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckListItemResponse:
    """Create a new item in a checklist."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    new_item = await checklist_service.create_checklist_item(
        db=db, checklist_id=checklist_id, text=item_data.text
    )
    return CheckListItemResponse.model_validate(new_item)


@router.patch("/{checklist_id}/items/{item_id}", response_model=CheckListItemResponse)
async def update_checklist_item(
    checklist_id: UUID,
    item_id: UUID,
    item_data: CheckListItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckListItemResponse:
    """Update a checklist item."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    try:
        updated_item = await checklist_service.update_checklist_item(
            db=db,
            item_id=item_id,
            text=item_data.text,
            completed=item_data.completed,
            order_index=item_data.order_index,
        )
        return CheckListItemResponse.model_validate(updated_item)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CheckListItem not found") from None


@router.delete("/{checklist_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_checklist_item(
    checklist_id: UUID,
    item_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a checklist item."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    try:
        await checklist_service.delete_checklist_item(db=db, item_id=item_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CheckListItem not found") from None


@router.post("/{checklist_id}/items/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_checklist_items(
    checklist_id: UUID,
    reorder_data: list[CheckListItemReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Reorder items in a checklist."""
    # Verify ownership
    if not await checklist_service.verify_checklist_ownership(db=db, checklist_id=checklist_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found")

    reorder_list = [{"id": item.id, "order_index": item.order_index} for item in reorder_data]
    await checklist_service.reorder_checklist_items(db=db, reorder_data=reorder_list)
