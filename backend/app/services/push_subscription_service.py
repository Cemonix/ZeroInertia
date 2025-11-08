"""Service for managing push notification subscriptions."""
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.push_subscription import PushSubscription
from app.schemas.push_subscription import PushSubscriptionCreate


async def create_subscription(
    db: AsyncSession,
    user_id: UUID,
    subscription_data: PushSubscriptionCreate,
) -> PushSubscription:
    """
    Create or update a push subscription for a user.
    If the endpoint (FCM token) already exists, update it (upsert behavior).

    Args:
        db: Database session
        user_id: User UUID
        subscription_data: Subscription data from frontend (FCM token)

    Returns:
        Created or updated PushSubscription
    """
    # Check if subscription with this endpoint already exists
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.endpoint == subscription_data.endpoint)
    )
    existing_subscription = result.scalar_one_or_none()

    if existing_subscription:
        # Update existing subscription metadata
        existing_subscription.user_agent = subscription_data.user_agent
        await db.commit()
        await db.refresh(existing_subscription)
        logger.info(f"Updated push subscription {existing_subscription.id} for user {user_id}")
        return existing_subscription

    # Create new subscription
    new_subscription = PushSubscription(
        user_id=user_id,
        endpoint=subscription_data.endpoint,
        user_agent=subscription_data.user_agent,
    )

    db.add(new_subscription)
    await db.commit()
    await db.refresh(new_subscription)
    logger.info(f"Created push subscription {new_subscription.id} for user {user_id}")
    return new_subscription


async def get_user_subscriptions(db: AsyncSession, user_id: UUID) -> list[PushSubscription]:
    """
    Get all push subscriptions for a user.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        List of PushSubscription objects
    """
    result = await db.execute(
        select(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    return list(result.scalars().all())


async def delete_subscription(
    db: AsyncSession,
    user_id: UUID,
    endpoint: str,
) -> bool:
    """
    Delete a push subscription by endpoint.

    Args:
        db: Database session
        user_id: User UUID (for authorization)
        endpoint: Subscription endpoint to delete

    Returns:
        True if deleted, False if not found
    """
    result = await db.execute(
        delete(PushSubscription).where(
            PushSubscription.user_id == user_id,
            PushSubscription.endpoint == endpoint,
        )
    )
    await db.commit()

    deleted = result.rowcount > 0
    if deleted:
        logger.info(f"Deleted push subscription for user {user_id}, endpoint: {endpoint[:50]}...")
    else:
        logger.warning(f"No subscription found to delete for user {user_id}, endpoint: {endpoint[:50]}...")

    return deleted


async def delete_all_user_subscriptions(db: AsyncSession, user_id: UUID) -> int:
    """
    Delete all push subscriptions for a user.

    Args:
        db: Database session
        user_id: User UUID

    Returns:
        Number of subscriptions deleted
    """
    result = await db.execute(
        delete(PushSubscription).where(PushSubscription.user_id == user_id)
    )
    await db.commit()

    count = result.rowcount
    logger.info(f"Deleted {count} push subscriptions for user {user_id}")
    return count
