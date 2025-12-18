#!/usr/bin/env python3
"""
Script to create inbox projects for existing users who don't have one.
Run this once after deploying the inbox feature.

Usage:
    docker exec zero_inertia_backend python scripts/create_missing_inboxes.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.core.database import async_session_local
from app.core.seed import create_inbox_project
from app.models.project import Project
from app.models.user import User


async def create_missing_inboxes():
    """Create inbox projects for all users who don't have one."""
    async with async_session_local() as session:
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()

        print(f"Found {len(users)} users")

        for user in users:
            # Check if user already has an inbox
            inbox_result = await session.execute(
                select(Project).where(
                    Project.user_id == user.id,
                    Project.is_inbox.is_(True)
                )
            )
            inbox = inbox_result.scalars().first()

            if inbox:
                print(f"✓ User {user.email} already has inbox: {inbox.title}")
            else:
                print(f"✗ User {user.email} missing inbox, creating...")
                inbox = await create_inbox_project(session, user.id)
                print(f"  ✓ Created inbox: {inbox.title} (ID: {inbox.id})")

        print("\nDone!")


if __name__ == "__main__":
    asyncio.run(create_missing_inboxes())
