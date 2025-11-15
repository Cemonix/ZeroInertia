from uuid import UUID

from fastapi import Depends, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.api.v1.pagination_deps import get_pagination_params
from app.core.database import get_db
from app.core.exceptions import NoteNotFoundException
from app.models.user import User
from app.schemas.note import NoteCreate, NoteReorder, NoteResponse, NoteUpdate
from app.schemas.pagination import PaginatedResponse, PaginationParams
from app.services import note_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[NoteResponse])
async def list_notes(
    pagination: PaginationParams = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[NoteResponse]:
    """Return notes for the authenticated user with pagination."""
    notes, total = await note_service.get_notes(
        db=db,
        user_id=current_user.id,
        skip=pagination.offset,
        limit=pagination.limit,
    )

    note_responses = [NoteResponse.model_validate(note) for note in notes]
    return PaginatedResponse[NoteResponse].create(
        items=note_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Create a new note for the authenticated user."""
    note = await note_service.create_note(
        db=db,
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        parent_id=note_data.parent_id,
        order_index=note_data.order_index,
    )
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
        raise NoteNotFoundException(str(note_id))
    return NoteResponse.model_validate(note)


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteResponse:
    """Update a note for the authenticated user."""
    note = await note_service.update_note(
        db=db,
        note_id=note_id,
        user_id=current_user.id,
        update_data=note_data,
    )
    return NoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a note for the authenticated user."""
    await note_service.delete_note(db=db, note_id=note_id, user_id=current_user.id)


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_notes(
    notes_reorder: list[NoteReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Update parent and order indices for a set of notes."""
    await note_service.reorder_notes(
        db=db,
        user_id=current_user.id,
        notes_reorder=notes_reorder,
    )
