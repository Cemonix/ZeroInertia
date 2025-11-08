from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PushSubscriptionCreate(BaseModel):
    """Schema for creating a push subscription from browser (FCM token)"""
    endpoint: str = Field(..., description="FCM registration token")
    user_agent: str | None = Field(None, max_length=500, description="Browser/device user agent")

    model_config: ClassVar[ConfigDict] = ConfigDict(json_schema_extra={
        "example": {
            "endpoint": "fcm_token_here...",
            "user_agent": "Mozilla/5.0..."
        }
    })


class PushSubscriptionResponse(BaseModel):
    """Schema for push subscription responses"""
    id: UUID
    user_id: UUID
    endpoint: str
    user_agent: str | None
    created_at: datetime
    updated_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)
