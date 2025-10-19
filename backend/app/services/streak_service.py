from datetime import date, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.models.streak import Streak


async def get_or_create_user_streak(db: AsyncSession, user_id: UUID) -> Streak:
    """Get user's streak record, creating one if it doesn't exist."""
    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id)
    )
    streak = result.scalars().first()

    if not streak:
        streak = Streak(
            user_id=user_id,
            current_streak=0,
            longest_streak=0,
            last_activity_date=None
        )
        db.add(streak)
        await db.commit()
        await db.refresh(streak)

    return streak


async def update_streak_on_completion(db: AsyncSession, user_id: UUID) -> Streak:
    """
    Update user's streak when they complete a task.
    Called immediately after a task is marked as complete.

    Logic:
    - If already updated today: do nothing (return current streak)
    - If last activity was yesterday: increment streak (consecutive day)
    - If last activity was before yesterday: reset streak to 1 (gap in days)
    - Update longest_streak if current exceeds it
    """
    streak = await get_or_create_user_streak(db, user_id)

    today = date.today()
    if streak.last_activity_date == today:
        return streak

    yesterday = today - timedelta(days=1)
    if streak.last_activity_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_activity_date = today
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak

    db.add(streak)
    await db.commit()
    await db.refresh(streak)

    return streak


async def reset_inactive_streaks(db: AsyncSession) -> int:
    """
    Reset streaks for users who didn't complete tasks yesterday.
    This should be called by a background job at midnight.

    Returns:
        Number of streaks reset
    """
    yesterday = date.today() - timedelta(days=1)

    # Find all streaks that:
    # 1. Have a current_streak > 0 (active streaks)
    # 2. last_activity_date is before yesterday (missed a day)
    result = await db.execute(
        select(Streak).where(
            Streak.current_streak > 0,
            Streak.last_activity_date < yesterday
        )
    )

    streaks_to_reset = result.scalars().all()

    for streak in streaks_to_reset:
        streak.current_streak = 0

    await db.commit()

    return len(streaks_to_reset)
