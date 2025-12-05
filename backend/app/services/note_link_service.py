import re
from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models.note import Note
from app.models.note_link import NoteLink
from app.schemas.note_link import BacklinkInfo


def extract_wikilinks(content: str) -> list[str]:
    """
    Extract [[wikilink]] style note titles from markdown content.

    Args:
        content: Markdown content to parse

    Returns:
        List of note titles referenced in the content
    """
    pattern = r'\[\[([^\]]+)\]\]'
    matches: list[str] = re.findall(pattern, content)
    return [str(match).strip() for match in matches if str(match).strip()]


async def sync_note_links(
    db: AsyncSession,
    source_note_id: UUID,
    user_id: UUID,
    content: str,
) -> None:
    """
    Synchronize note links based on [[wikilinks]] in note content.

    This function:
    1. Extracts all [[Note Title]] references from content
    2. Finds matching notes by title (user-scoped)
    3. Deletes old links that are no longer in content
    4. Creates new links that don't exist yet

    Args:
        db: Database session
        source_note_id: ID of the note being updated
        user_id: User ID (for scoping note lookups)
        content: Note markdown content
    """
    wikilink_titles = extract_wikilinks(content)

    if not wikilink_titles:
        _ = await db.execute(
            delete(NoteLink).where(NoteLink.source_note_id == source_note_id)
        )
        return

    result = await db.execute(
        select(Note.id, Note.title)
        .where(
            Note.user_id == user_id,
            func.lower(Note.title).in_([title.lower() for title in wikilink_titles]),
            Note.id != source_note_id,
        )
    )
    target_notes: list[tuple[UUID, str]] = result.all()  # pyright: ignore[reportAssignmentType]
    target_note_ids: set[UUID] = {note_id for note_id, _ in target_notes}

    existing_links_result = await db.execute(
        select(NoteLink.target_note_id)
        .where(NoteLink.source_note_id == source_note_id)
    )
    existing_target_ids: set[UUID] = {UUID(str(row[0])) for row in existing_links_result.all()}  # pyright: ignore[reportAny]

    links_to_delete = existing_target_ids - target_note_ids
    if links_to_delete:
        _ = await db.execute(
            delete(NoteLink).where(
                NoteLink.source_note_id == source_note_id,
                NoteLink.target_note_id.in_(list(links_to_delete)),
            )
        )

    links_to_create = target_note_ids - existing_target_ids
    for target_id in links_to_create:
        new_link = NoteLink(
            source_note_id=source_note_id,
            target_note_id=target_id,
        )
        db.add(new_link)


async def get_backlinks(
    db: AsyncSession,
    note_id: UUID,
    user_id: UUID,
) -> Sequence[BacklinkInfo]:
    """
    Get all notes that link to the specified note.

    Args:
        db: Database session
        note_id: ID of the note to find backlinks for
        user_id: User ID for authorization check

    Returns:
        List of BacklinkInfo with note ID, title, and link creation date
    """
    result = await db.execute(
        select(NoteLink, Note)
        .join(Note, Note.id == NoteLink.source_note_id)
        .where(
            NoteLink.target_note_id == note_id,
            Note.user_id == user_id,
        )
        .order_by(NoteLink.created_at.desc())
    )

    backlinks: list[BacklinkInfo] = []
    rows: list[tuple[NoteLink, Note]] = result.all()  # pyright: ignore[reportAssignmentType]
    for link, note in rows:
        backlinks.append(
            BacklinkInfo(
                note_id=note.id,
                note_title=note.title,
                created_at=link.created_at,
            )
        )

    return backlinks
