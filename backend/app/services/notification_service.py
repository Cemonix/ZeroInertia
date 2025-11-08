"""
Push notification service using Firebase Cloud Messaging (FCM).
Handles sending Web Push notifications to subscribed browsers/devices.
"""
import asyncio
from pathlib import Path
from uuid import UUID

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin import exceptions as firebase_exceptions
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.settings.app_settings import get_app_settings
from app.models.push_subscription import PushSubscription

# Initialize Firebase Admin SDK
_firebase_app: firebase_admin.App | None = None

# Retry configuration (simple exponential backoff)
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1.0  # seconds
BACKOFF_MULTIPLIER = 2.0


def _send_fcm_message_sync(
    fcm_token: str,
    title: str,
    body: str,
    frontend_url: str,
    data: dict[str, str] | None = None,
) -> str:
    """
    Synchronous FCM message sending - to be wrapped in asyncio.to_thread().

    Args:
        fcm_token: FCM registration token
        title: Notification title
        body: Notification body
        frontend_url: Frontend URL for icon/badge
        data: Optional custom data payload

    Returns:
        Message ID from FCM

    Raises:
        firebase_exceptions.FirebaseError: On FCM errors
    """
    # Build the notification
    notification_payload = messaging.Notification(
        title=title,
        body=body,
    )

    # Web push specific configuration
    webpush_config = messaging.WebpushConfig(
        headers={
            "TTL": "86400",  # 24 hours time-to-live
        },
        notification=messaging.WebpushNotification(
            title=title,
            body=body,
            icon=f"{frontend_url}/ZeroInertia.svg",
            badge=f"{frontend_url}/ZeroInertia.svg",
        ),
        data=data or {},
    )

    # Build and send the complete message
    message = messaging.Message(
        notification=notification_payload,
        webpush=webpush_config,
        token=fcm_token,
    )

    return messaging.send(message)


async def _send_push_notification_with_retry(
    subscription: PushSubscription,
    title: str,
    body: str,
    frontend_url: str,
    data: dict[str, str] | None = None,
    attempt: int = 1,
) -> tuple[bool, str | None]:
    """
    Send push notification with simple exponential backoff retry logic.

    Args:
        subscription: PushSubscription model instance
        title: Notification title
        body: Notification body
        frontend_url: Frontend URL for icons
        data: Optional data payload
        attempt: Current attempt number (1-indexed)

    Returns:
        Tuple of (success: bool, error_code: str | None)
    """
    try:
        # Run synchronous Firebase call in thread pool
        response = await asyncio.to_thread(
            _send_fcm_message_sync,
            subscription.endpoint,
            title,
            body,
            frontend_url,
            data,
        )

        logger.info(f"Successfully sent notification to subscription {subscription.id}: {response}")
        return True, None

    except firebase_exceptions.FirebaseError as e:
        error_code = e.code if hasattr(e, "code") else None

        # Identify token issues for cleanup (no retry for these)
        if error_code in ("invalid-registration-token", "registration-token-not-registered"):
            logger.error(
                f"Invalid FCM token for subscription {subscription.id}: {e}"
            )
            return False, "invalid_token"

        # Retry on transient errors (network issues, FCM unavailable, quota exceeded)
        if attempt < MAX_RETRIES and error_code in ("unavailable", "internal", "quota-exceeded"):
            delay = INITIAL_RETRY_DELAY * (BACKOFF_MULTIPLIER ** (attempt - 1))
            logger.warning(
                f"Transient error sending notification (attempt {attempt}/{MAX_RETRIES}), " +
                f"retrying in {delay}s: {e}"
            )
            await asyncio.sleep(delay)
            return await _send_push_notification_with_retry(
                subscription, title, body, frontend_url, data, attempt + 1
            )

        logger.error(
            f"Firebase error sending notification to subscription {subscription.id} " +
            f"(attempt {attempt}/{MAX_RETRIES}): {e} (code: {error_code})"
        )
        return False, error_code  # pyright: ignore[reportUnknownVariableType]

    except Exception as e:
        # Retry on unexpected errors (network timeouts, etc.)
        if attempt < MAX_RETRIES:
            delay = INITIAL_RETRY_DELAY * (BACKOFF_MULTIPLIER ** (attempt - 1))
            logger.warning(
                f"Unexpected error sending notification (attempt {attempt}/{MAX_RETRIES}), " +
                f"retrying in {delay}s: {e}"
            )
            await asyncio.sleep(delay)
            return await _send_push_notification_with_retry(
                subscription, title, body, frontend_url, data, attempt + 1
            )

        logger.error(
            f"Unexpected error sending notification to subscription {subscription.id} " +
            f"(attempt {attempt}/{MAX_RETRIES}): {e}"
        )
        return False, None


async def send_push_notification(
    subscription: PushSubscription,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> tuple[bool, str | None]:
    """
    Send a push notification to a specific subscription using FCM.
    Includes automatic retry with exponential backoff for transient errors.

    NOTE: The 'endpoint' field stores the FCM registration token from the frontend.

    Args:
        subscription: PushSubscription model instance (endpoint contains FCM token)
        title: Notification title
        body: Notification body text
        data: Optional custom data payload (must be string key-value pairs)

    Returns:
        Tuple of (success: bool, error_code: str | None)
        error_code is set for token expiry/invalidity issues
    """
    # Initialize Firebase if not already done
    _ = _initialize_firebase()

    # Get settings for frontend URL
    settings = get_app_settings()
    frontend_url = settings.cors_origins[0] if settings.cors_origins else "http://localhost:5173"

    return await _send_push_notification_with_retry(
        subscription, title, body, frontend_url, data
    )


async def send_notification_to_user(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> int:
    """
    Send push notification to all of a user's subscribed devices.
    Automatically cleans up invalid/expired FCM tokens.

    Args:
        db: Database session
        user_id: User UUID
        title: Notification title
        body: Notification body
        data: Optional custom data payload

    Returns:
        Number of successfully sent notifications
    """
    # Get all active subscriptions for the user
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    subscriptions = result.scalars().all()

    if not subscriptions:
        logger.info(f"No push subscriptions found for user {user_id}")
        return 0

    success_count = 0
    invalid_subscription_ids: list[UUID] = []

    for subscription in subscriptions:
        success, error_code = await send_push_notification(subscription, title, body, data)
        if success:
            success_count += 1
        elif error_code == "invalid_token":
            # Token is invalid or expired - mark for deletion
            invalid_subscription_ids.append(subscription.id)

    # Clean up invalid subscriptions
    if invalid_subscription_ids:
        result = await db.execute(
            delete(PushSubscription).where(PushSubscription.id.in_(invalid_subscription_ids))
        )
        await db.commit()
        deleted_count = result.rowcount
        logger.info(
            f"Cleaned up {deleted_count} invalid push subscriptions for user {user_id}. " +
            f"IDs: {invalid_subscription_ids}"
        )

    logger.info(f"Sent {success_count}/{len(subscriptions)} notifications to user {user_id}")
    return success_count


async def send_task_reminder(
    db: AsyncSession,
    user_id: UUID,
    task_title: str,
    task_id: UUID,
    due_datetime: str,
) -> int:
    """
    Send a task reminder notification to the user.

    Args:
        db: Database session
        user_id: User UUID
        task_title: Title of the task
        task_id: Task UUID (for navigation)
        due_datetime: Formatted due date/time string

    Returns:
        Number of successfully sent notifications
    """
    title = "Task Reminder"
    body = f"{task_title} is due {due_datetime}"
    data = {
        "type": "task_reminder",
        "task_id": str(task_id),
        "task_title": task_title,
    }

    return await send_notification_to_user(db, user_id, title, body, data)


def _initialize_firebase() -> firebase_admin.App:
    """Initialize Firebase Admin SDK with service account credentials."""
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    settings = get_app_settings()
    service_account_path = Path(settings.firebase_service_account_path)

    # Make path relative to backend directory if not absolute
    if not service_account_path.is_absolute():
        backend_dir = Path(__file__).parent.parent.parent  # Go up to backend/
        service_account_path = backend_dir / service_account_path

    if not service_account_path.exists():
        raise FileNotFoundError(
            f"Firebase service account file not found: {service_account_path}. " +
            "Please ensure FIREBASE_SERVICE_ACCOUNT_PATH is set correctly in .env"
        )

    cred = credentials.Certificate(str(service_account_path))
    _firebase_app = firebase_admin.initialize_app(cred)  # pyright: ignore[reportUnknownMemberType]
    logger.info(f"Firebase Admin SDK initialized with service account: {service_account_path}")

    return _firebase_app
