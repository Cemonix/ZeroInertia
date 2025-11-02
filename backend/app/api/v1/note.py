from typing import cast
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.note import NoteCreate, NoteReorder, NoteResponse, NoteUpdate
from app.services import note_service

router = APIRouter()


@router.get("/", response_model=list[NoteResponse])
async def list_notes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[NoteResponse]:
    """Return all notes for the authenticated user."""
    notes = await note_service.get_notes(db=db, user_id=current_user.id)
    return [NoteResponse.model_validate(note) for note in notes]


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Create a new note for the authenticated user."""
    try:
        note = await note_service.create_note(
            db=db,
            user_id=current_user.id,
            title=note_data.title,
            content=note_data.content,
            parent_id=note_data.parent_id,
            order_index=note_data.order_index,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return NoteResponse.model_validate(note)


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Return a single note for the authenticated user."""
    note = await note_service.get_note_by_id(db=db, note_id=note_id, user_id=current_user.id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return NoteResponse.model_validate(note)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Update a note for the authenticated user."""
    payload = note_data.model_dump(exclude_unset=True)
    parent_id_set = "parent_id" in payload
    parent_id = cast(UUID | None, payload.pop("parent_id", None))
    try:
        note = await note_service.update_note(
            db=db,
            note_id=note_id,
            user_id=current_user.id,
            parent_id=parent_id,
            parent_id_set=parent_id_set,
            **payload,  # pyright: ignore[reportAny]
        )
    except ValueError as exc:
        message = str(exc)
        if message == "Note not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message) from exc
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message) from exc
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a note for the authenticated user."""
    try:
        await note_service.delete_note(db=db, note_id=note_id, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found") from None


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_notes(
    notes_reorder: list[NoteReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Update parent and order indices for a set of notes."""
    try:
        await note_service.reorder_notes(
            db=db,
            user_id=current_user.id,
            notes_reorder=notes_reorder,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
