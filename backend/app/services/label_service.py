from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.exceptions import DuplicateResourceException, LabelNotFoundException
from app.models.label import Label


async def create_label(
    db: AsyncSession,
    user_id: UUID,
    name: str,
    color: str | None,
    description: str | None,
    order_index: int | None,
) -> Label:
    """Create a new label for the user."""
    if order_index is None:
        order_index = await _get_next_order_index(db, user_id)

    new_label = Label(
        user_id=user_id,
        name=name,
        color=color,
        description=description,
        order_index=order_index,
    )
    db.add(new_label)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateResourceException("Label", f"name '{name}'") from exc

    await db.refresh(new_label)
    return new_label


async def get_labels(db: AsyncSession, user_id: UUID) -> Sequence[Label]:
    """Return all labels belonging to the user ordered by order_index."""
    result = await db.execute(
        select(Label)
        .where(Label.user_id == user_id)
        .order_by(Label.order_index, Label.created_at)
    )
    return result.scalars().all()


async def get_label_by_id(db: AsyncSession, label_id: UUID, user_id: UUID) -> Label | None:
    """Return a label by id scoped to the user."""
    result = await db.execute(
        select(Label).where(Label.id == label_id, Label.user_id == user_id)
    )
    return result.scalars().first()


async def update_label(
    db: AsyncSession,
    label_id: UUID,
    user_id: UUID,
    name: str | None = None,
    color: str | None = None,
    description: str | None = None,
    order_index: int | None = None,
) -> Label:
    """Update an existing label."""
    label = await get_label_by_id(db, label_id, user_id)
    if label is None:
        raise LabelNotFoundException(str(label_id))

    if name is not None:
        label.name = name
    if color is not None:
        label.color = color
    if description is not None:
        label.description = description
    if order_index is not None:
        label.order_index = order_index

    db.add(label)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateResourceException("Label", f"name '{name}'") from exc

    await db.refresh(label)
    return label


async def delete_label(db: AsyncSession, label_id: UUID, user_id: UUID) -> None:
    """Delete a label."""
    label = await get_label_by_id(db, label_id, user_id)
    if label is None:
        raise LabelNotFoundException(str(label_id))

    await db.delete(label)
    await db.commit()


async def _get_next_order_index(db: AsyncSession, user_id: UUID) -> int:
    """Return the next order index for the user's labels."""
    result = await db.execute(
        select(Label.order_index)
        .where(Label.user_id == user_id)
        .order_by(Label.order_index.desc())
        .limit(1)
    )
    max_order = result.scalar()
    return (max_order + 1) if max_order is not None else 0
