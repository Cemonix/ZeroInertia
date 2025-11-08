from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import select

from app.core.exceptions import ChecklistItemNotFoundException, ChecklistNotFoundException
from app.models.checklist import CheckList, CheckListItem
from app.models.task import Task


async def verify_checklist_ownership(
    db: AsyncSession, checklist_id: UUID, user_id: UUID
) -> bool:
    """Verify that a checklist belongs to a user by checking through the task."""
    result = await db.execute(
        select(CheckList)
        .join(Task, CheckList.task_id == Task.id)
        .where(CheckList.id == checklist_id, Task.user_id == user_id)
    )
    checklist = result.scalars().first()
    return checklist is not None

# ==============================================================================
# CheckList CRUD Operations
# ==============================================================================


async def create_checklist(
    db: AsyncSession, task_id: UUID, title: str
) -> CheckList:
    """Create a new checklist for a task."""
    # Get the max order_index for this task to append new checklist at the end
    result = await db.execute(
        select(CheckList.order_index)
        .where(CheckList.task_id == task_id)
        .order_by(CheckList.order_index.desc())
        .limit(1)
    )
    max_order = result.scalar()
    next_order_index = (max_order + 1) if max_order is not None else 0

    new_checklist = CheckList(
        task_id=task_id, title=title, order_index=next_order_index
    )
    db.add(new_checklist)
    await db.commit()
    await db.refresh(new_checklist, ["items"])
    return new_checklist


async def get_checklist_by_id(db: AsyncSession, checklist_id: UUID) -> CheckList | None:
    """Retrieve a checklist by its ID with all items loaded."""
    result = await db.execute(
        select(CheckList)
        .where(CheckList.id == checklist_id)
        .options(selectinload(CheckList.items))
    )
    return result.scalars().first()


async def get_checklists_by_task(db: AsyncSession, task_id: UUID) -> Sequence[CheckList]:
    """Retrieve all checklists for a specific task."""
    result = await db.execute(
        select(CheckList)
        .where(CheckList.task_id == task_id)
        .options(selectinload(CheckList.items))
        .order_by(CheckList.order_index)
    )
    return result.scalars().all()


async def update_checklist(
    db: AsyncSession,
    checklist_id: UUID,
    title: str | None = None,
    order_index: int | None = None,
) -> CheckList:
    """Update a checklist."""
    checklist = await get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise ChecklistNotFoundException(str(checklist_id))

    if title is not None:
        checklist.title = title
    if order_index is not None:
        checklist.order_index = order_index

    await db.commit()
    await db.refresh(checklist)
    return checklist


async def delete_checklist(db: AsyncSession, checklist_id: UUID) -> None:
    """Delete a checklist and all its items (cascade)."""
    checklist = await get_checklist_by_id(db, checklist_id)
    if not checklist:
        raise ChecklistNotFoundException(str(checklist_id))

    await db.delete(checklist)
    await db.commit()


async def reorder_checklists(db: AsyncSession, reorder_data: list[dict[str, UUID | int]]) -> None:
    """Reorder checklists by updating their order_index."""
    for item in reorder_data:
        checklist_id = item["id"]
        new_order_index = item["order_index"]

        if isinstance(checklist_id, int):
            continue  # Skip invalid IDs

        if isinstance(new_order_index, UUID):
            continue  # Skip invalid order_index

        checklist = await get_checklist_by_id(db, checklist_id)  # type: ignore
        if checklist:
            checklist.order_index = new_order_index  # type: ignore

    await db.commit()


# ==============================================================================
# CheckListItem CRUD Operations
# ==============================================================================


async def create_checklist_item(
    db: AsyncSession, checklist_id: UUID, text: str
) -> CheckListItem:
    """Create a new checklist item."""
    # Get the max order_index for this checklist to append new item at the end
    result = await db.execute(
        select(CheckListItem.order_index)
        .where(CheckListItem.checklist_id == checklist_id)
        .order_by(CheckListItem.order_index.desc())
        .limit(1)
    )
    max_order = result.scalar()
    next_order_index = (max_order + 1) if max_order is not None else 0

    new_item = CheckListItem(
        checklist_id=checklist_id,
        text=text,
        completed=False,
        order_index=next_order_index,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


async def get_checklist_item_by_id(
    db: AsyncSession, item_id: UUID
) -> CheckListItem | None:
    """Retrieve a checklist item by its ID."""
    result = await db.execute(select(CheckListItem).where(CheckListItem.id == item_id))
    return result.scalars().first()


async def update_checklist_item(
    db: AsyncSession,
    item_id: UUID,
    text: str | None = None,
    completed: bool | None = None,
    order_index: int | None = None,
) -> CheckListItem:
    """Update a checklist item."""
    item = await get_checklist_item_by_id(db, item_id)
    if not item:
        raise ChecklistItemNotFoundException(str(item_id))

    if text is not None:
        item.text = text
    if completed is not None:
        item.completed = completed
    if order_index is not None:
        item.order_index = order_index

    await db.commit()
    await db.refresh(item)
    return item


async def delete_checklist_item(db: AsyncSession, item_id: UUID) -> None:
    """Delete a checklist item."""
    item = await get_checklist_item_by_id(db, item_id)
    if not item:
        raise ChecklistItemNotFoundException(str(item_id))

    await db.delete(item)
    await db.commit()


async def reorder_checklist_items(
    db: AsyncSession, reorder_data: list[dict[str, UUID | int]]
) -> None:
    """Reorder checklist items by updating their order_index."""
    for item_data in reorder_data:
        item_id = item_data["id"]
        new_order_index = item_data["order_index"]

        if isinstance(item_id, int):
            continue  # Skip invalid IDs

        if isinstance(new_order_index, UUID):
            continue  # Skip invalid order_index

        item = await get_checklist_item_by_id(db, item_id)  # type: ignore
        if item:
            item.order_index = new_order_index  # type: ignore

    await db.commit()
