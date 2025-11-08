"""API endpoints for push notification management."""
from fastapi import Depends, status
from fastapi.routing import APIRouter
from pydantic import BaseModel
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.v1.auth_deps import get_current_user
from app.core.database import get_db
from app.core.exceptions import PushSubscriptionNotFoundException
from app.core.logging import logger
from app.models.user import User
from app.schemas.push_subscription import PushSubscriptionCreate, PushSubscriptionResponse
from app.services import notification_service, push_subscription_service

router = APIRouter()


class TestNotificationRequest(BaseModel):
    """Schema for test notification requests."""
    title: str
    body: str


@router.post("/subscribe", response_model=PushSubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_push(
    subscription_data: PushSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PushSubscriptionResponse:
    """
    Subscribe to push notifications.
    Creates or updates a push subscription for the authenticated user.
    """
    subscription = await push_subscription_service.create_subscription(
        db=db,
        user_id=current_user.id,
        subscription_data=subscription_data,
    )
    return PushSubscriptionResponse.model_validate(subscription)


@router.post("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_push(
    subscription_data: PushSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Unsubscribe from push notifications.
    Deletes a specific push subscription by endpoint (FCM token).
    """
    deleted = await push_subscription_service.delete_subscription(
        db=db,
        user_id=current_user.id,
        endpoint=subscription_data.endpoint,
    )

    if not deleted:
        raise PushSubscriptionNotFoundException()


@router.get("/subscriptions", response_model=list[PushSubscriptionResponse])
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PushSubscriptionResponse]:
    """Get all push subscriptions for the authenticated user."""
    subscriptions = await push_subscription_service.get_user_subscriptions(
        db=db,
        user_id=current_user.id,
    )
    return [PushSubscriptionResponse.model_validate(sub) for sub in subscriptions]


@router.delete("/subscriptions/all", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete all push subscriptions for the authenticated user."""
    count = await push_subscription_service.delete_all_user_subscriptions(
        db=db,
        user_id=current_user.id,
    )
    logger.info(f"Deleted {count} push subscriptions for user {current_user.id}")


@router.post("/test", status_code=status.HTTP_200_OK)
async def send_test_notification(
    request: TestNotificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    """
    Send a test notification immediately to the authenticated user.
    Useful for testing notification setup without waiting for scheduled reminders.

    Note: If title is not provided, defaults to a sample task title format.
    """
    # Use provided title/body, or default to task reminder format for testing
    title = request.title if request.title else "Sample Task Name"
    body = request.body if request.body else "Due in 30 minutes"

    count = await notification_service.send_notification_to_user(
        db=db,
        user_id=current_user.id,
        title=title,
        body=body,
        data={"type": "test"},
    )

    if count == 0:
        raise PushSubscriptionNotFoundException()

    return {"sent": count}
