from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.section import SectionCreate, SectionReorder, SectionResponse, SectionUpdate
from app.services import section_service

router = APIRouter()


@router.post("/", response_model=SectionResponse, status_code=status.HTTP_201_CREATED)
async def create_section(
    section_data: SectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SectionResponse:
    """Create a new section for the authenticated user."""
    new_section = await section_service.create_section(
        db=db,
        user_id=current_user.id,
        title=section_data.title,
        project_id=section_data.project_id,
        order_index=section_data.order_index,
    )
    return SectionResponse.model_validate(new_section)


@router.get("/", response_model=list[SectionResponse], status_code=status.HTTP_200_OK)
async def get_sections(
    project_id: UUID | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SectionResponse]:
    """Get all sections for the authenticated user."""
    if project_id:
        sections = await section_service.get_sections_by_project(
            db=db,
            user_id=current_user.id,
            project_id=project_id
        )
    else:
        sections = await section_service.get_sections(db=db, user_id=current_user.id)
    return [SectionResponse.model_validate(section) for section in sections]


@router.get("/{section_id}", response_model=SectionResponse, status_code=status.HTTP_200_OK)
async def get_section(
    section_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SectionResponse:
    """Get a specific section by ID for the authenticated user."""
    section = await section_service.get_section_by_id(db=db, section_id=section_id, user_id=current_user.id)
    if not section:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found")
    return SectionResponse.model_validate(section)


@router.patch("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_sections(
    sections_reorder: list[SectionReorder],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Batch update section order."""
    try:
        await section_service.reorder_sections(
            db=db,
            user_id=current_user.id,
            sections_reorder=sections_reorder
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more sections not found") from None


@router.patch(
    "/{section_id}",
    response_model=SectionResponse,
    status_code=status.HTTP_200_OK
)
async def update_section(
    section_id: UUID,
    section_data: SectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SectionResponse:
    """Update a specific section by ID for the authenticated user."""
    try:
        updated_section = await section_service.update_section(
            db=db,
            section_id=section_id,
            user_id=current_user.id,
            title=section_data.title,
            order_index=section_data.order_index,
        )
        return SectionResponse.model_validate(updated_section)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found") from None


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_section(
    section_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a specific section by ID for the authenticated user."""
    try:
        await section_service.delete_section(db=db, section_id=section_id, user_id=current_user.id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Section not found") from None
