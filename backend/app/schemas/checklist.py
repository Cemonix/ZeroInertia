from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# CheckListItem Schemas
# ============================================================================


class CheckListItemCreate(BaseModel):
    """Schema for creating a checklist item"""

    text: str = Field(..., min_length=1)


class CheckListItemUpdate(BaseModel):
    """Schema for updating a checklist item"""

    text: str | None = Field(None, min_length=1)
    completed: bool | None = None
    order_index: int | None = None


class CheckListItemResponse(BaseModel):
    """Schema for checklist item responses"""

    id: UUID
    checklist_id: UUID
    text: str
    completed: bool
    order_index: int
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class CheckListItemReorder(BaseModel):
    """Schema for reordering checklist items"""

    id: UUID
    order_index: int


# ============================================================================
# CheckList Schemas
# ============================================================================


class CheckListCreate(BaseModel):
    """Schema for creating a checklist"""

    task_id: UUID
    title: str = Field(..., min_length=1, max_length=255)


class CheckListUpdate(BaseModel):
    """Schema for updating a checklist"""

    title: str | None = Field(None, min_length=1, max_length=255)
    order_index: int | None = None


class CheckListResponse(BaseModel):
    """Schema for checklist responses"""

    id: UUID
    task_id: UUID
    title: str
    order_index: int
    created_at: datetime
    updated_at: datetime
    items: list[CheckListItemResponse] = Field(default_factory=list)

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class CheckListReorder(BaseModel):
    """Schema for reordering checklists"""

    id: UUID
    order_index: int
