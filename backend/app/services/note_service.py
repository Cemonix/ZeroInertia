from collections.abc import Sequence
from typing import cast
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.exceptions import InvalidOperationException, NoteNotFoundException
from app.models.note import Note
from app.schemas.note import NoteReorder, NoteUpdate
from app.services import note_link_service
from app.services.base_service import apply_updates_async


async def _ensure_parent_belongs_to_user(
    db: AsyncSession,
    user_id: UUID,
    parent_id: UUID | None,
) -> None:
    """Validate that the parent note exists and belongs to the user."""
    if parent_id is None:
        return

    result = await db.execute(
        select(Note.id).where(Note.id == parent_id, Note.user_id == user_id)
    )
    if result.scalar_one_or_none() is None:
        raise NoteNotFoundException(str(parent_id))


async def _next_order_index(
    db: AsyncSession,
    user_id: UUID,
    parent_id: UUID | None,
) -> int:
    """Calculate the next order index within a parent group."""
    parent_clause = Note.parent_id.is_(None) if parent_id is None else Note.parent_id == parent_id
    result = await db.execute(
        select(func.max(Note.order_index)).where(
            Note.user_id == user_id,
            parent_clause,
        )
    )
    max_order = result.scalar()
    if max_order is None:
        return 0
    return max_order + 1


async def create_note(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    content: str,
    parent_id: UUID | None = None,
    order_index: int | None = None,
) -> Note:
    """Create a new note for the given user."""
    await _ensure_parent_belongs_to_user(db=db, user_id=user_id, parent_id=parent_id)

    if order_index is None:
        order_index = await _next_order_index(db=db, user_id=user_id, parent_id=parent_id)

    new_note = Note(
        user_id=user_id,
        title=title,
        content=content,
        parent_id=parent_id,
        order_index=order_index,
    )
    db.add(new_note)
    await db.flush()

    await note_link_service.sync_note_links(
        db=db,
        source_note_id=new_note.id,
        user_id=user_id,
        content=content,
    )

    await db.commit()
    await db.refresh(new_note)
    return new_note


async def get_note_by_id(
    db: AsyncSession,
    note_id: UUID,
    user_id: UUID,
) -> Note | None:
    """Return a specific note for the user."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    return result.scalars().first()


async def get_notes(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50,
) -> tuple[Sequence[Note], int]:
    """
    Return notes for the given user with pagination.

    Args:
        db: Database session
        user_id: User ID to filter notes
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return

    Returns:
        Tuple of (notes, total_count)
    """
    # Count total notes
    count_result = await db.execute(
        select(func.count(Note.id)).where(Note.user_id == user_id)
    )
    total = count_result.scalar_one()

    # Get paginated notes
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user_id)
        .order_by(Note.parent_id, Note.order_index, Note.created_at)
        .offset(skip)
        .limit(limit)
    )
    notes = result.scalars().all()

    return notes, total


async def update_note(
    db: AsyncSession,
    note_id: UUID,
    user_id: UUID,
    update_data: NoteUpdate,
) -> Note:
    """Update the note with the supplied fields."""
    note = await get_note_by_id(db=db, note_id=note_id, user_id=user_id)
    if note is None:
        raise NoteNotFoundException(str(note_id))

    async def handle_parent_id(_model: object, value: object, _updates: dict[str, object]) -> None:
        parent_id = cast(UUID | None, value)
        if parent_id == note.id:
            raise InvalidOperationException("Note cannot reference itself as parent")
        if parent_id is not None:
            await _ensure_parent_belongs_to_user(db=db, user_id=user_id, parent_id=parent_id)
        note.parent_id = parent_id

    _ = await apply_updates_async(
        model=note,
        update_schema=update_data,
        custom_handlers={"parent_id": handle_parent_id}
    )

    db.add(note)

    if update_data.content is not None:
        await note_link_service.sync_note_links(
            db=db,
            source_note_id=note.id,
            user_id=user_id,
            content=note.content,
        )

    await db.commit()
    await db.refresh(note)
    return note


async def delete_note(
    db: AsyncSession,
    note_id: UUID,
    user_id: UUID,
) -> None:
    """Remove a note and its descendants."""
    note = await get_note_by_id(db=db, note_id=note_id, user_id=user_id)
    if note is None:
        raise NoteNotFoundException(str(note_id))

    await db.delete(note)
    await db.commit()


async def reorder_notes(
    db: AsyncSession,
    user_id: UUID,
    notes_reorder: list[NoteReorder],
) -> None:
    """Update parent and order positions for a batch of notes."""
    note_ids = [note.id for note in notes_reorder]

    result = await db.execute(
        select(Note).where(
            Note.id.in_(note_ids),
            Note.user_id == user_id,
        )
    )
    notes_map = {note.id: note for note in result.scalars().all()}

    if len(notes_map) != len(note_ids):
        raise NoteNotFoundException()

    # Validate parent ownership in reorder payload
    parent_ids = {nr.parent_id for nr in notes_reorder if nr.parent_id is not None}
    if parent_ids:
        parent_check = await db.execute(
            select(Note.id).where(
                Note.id.in_(list(parent_ids)),
                Note.user_id == user_id,
            )
        )
        found_parent_ids = set(parent_check.scalars().all())
        if found_parent_ids != parent_ids:
            raise NoteNotFoundException()

    for note_data in notes_reorder:
        note = notes_map[note_data.id]
        if note_data.id == note_data.parent_id:
            raise InvalidOperationException("Note cannot reference itself as parent")
        note.parent_id = note_data.parent_id
        note.order_index = note_data.order_index
        db.add(note)

    await db.commit()
