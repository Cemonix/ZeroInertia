from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NoteLinkResponse(BaseModel):
    """Schema returned for note link entities."""

    id: UUID
    source_note_id: UUID
    target_note_id: UUID
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class BacklinkInfo(BaseModel):
    """Information about a note that links to the current note."""

    note_id: UUID
    note_title: str
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
