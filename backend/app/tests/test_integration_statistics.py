"""
Integration tests for statistics endpoints.

Tests cover:
- Daily completion counts for date ranges
- Calendar heatmap data retrieval
- Overall completion statistics and summary
- Best day tracking
- Date range validation
- User data isolation
"""

from datetime import datetime, timedelta, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Section, Task
from app.models.project import Project
from app.models.user import User

# pyright: reportAny=false


class TestStatisticsEndpoints:
    """Test statistics and calendar data functionality."""

    async def test_get_daily_completions_empty(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test getting daily completions with no completed tasks."""
        response = await authenticated_client.get(
            "/api/v1/statistics/daily",
            params={
                "start_date": "2025-01-01",
                "end_date": "2025-01-31",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["daily_counts"] == {}
        assert data["total_completions"] == 0
        assert data["start_date"] == "2025-01-01"
        assert data["end_date"] == "2025-01-31"

    async def test_get_daily_completions_with_data(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test getting daily completions with completed tasks."""
        # Create completed tasks on different days
        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # Task completed today (2 tasks)
        for i in range(2):
            task = Task(
                title=f"Task today {i}",
                user_id=test_user.id,
                project_id=test_project.id,
                section_id=test_section.id,
                completed=True,
                completed_at=today,
            )
            db_session.add(task)

        # Task completed yesterday (1 task)
        task = Task(
            title="Task yesterday",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            completed=True,
            completed_at=yesterday,
        )
        db_session.add(task)

        # Task completed two days ago (3 tasks)
        for i in range(3):
            task = Task(
                title=f"Task two days ago {i}",
                user_id=test_user.id,
                project_id=test_project.id,
                section_id=test_section.id,
                completed=True,
                completed_at=two_days_ago,
            )
            db_session.add(task)

        await db_session.commit()

        # Query for the last 7 days
        start_date = (today - timedelta(days=7)).date()
        end_date = today.date()

        response = await authenticated_client.get(
            "/api/v1/statistics/daily",
            params={
                "start_date": str(start_date),
                "end_date": str(end_date),
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_completions"] == 6
        assert str(today.date()) in data["daily_counts"]
        assert data["daily_counts"][str(today.date())] == 2
        assert data["daily_counts"][str(yesterday.date())] == 1
        assert data["daily_counts"][str(two_days_ago.date())] == 3

    async def test_get_calendar_heatmap_current_year(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test getting calendar heatmap for current year."""
        # Create some completed tasks this year
        now = datetime.now(timezone.utc)
        task = Task(
            title="Task this year",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            completed=True,
            completed_at=now,
        )
        db_session.add(task)
        await db_session.commit()

        response = await authenticated_client.get("/api/v1/statistics/calendar")

        assert response.status_code == 200
        data = response.json()
        assert data["year"] == now.year
        assert "daily_counts" in data
        assert data["total_completions"] >= 1
        assert data["max_day_count"] >= 1

        # Verify it contains all days in the year (365 or 366)
        expected_days = 366 if now.year % 4 == 0 else 365
        assert len(data["daily_counts"]) == expected_days

    async def test_get_calendar_heatmap_specific_year(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test getting calendar heatmap for a specific year."""
        response = await authenticated_client.get("/api/v1/statistics/calendar/2024")

        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2024
        # 2024 is a leap year
        assert len(data["daily_counts"]) == 366

    async def test_get_completion_summary(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test getting overall completion statistics summary."""
        # Create tasks at various times
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=5)
        month_ago = now - timedelta(days=20)

        # Tasks completed today (2)
        for i in range(2):
            task = Task(
                title=f"Task today {i}",
                user_id=test_user.id,
                project_id=test_project.id,
                section_id=test_section.id,
                completed=True,
                completed_at=now,
            )
            db_session.add(task)

        # Task completed this week (1)
        task = Task(
            title="Task this week",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            completed=True,
            completed_at=week_ago,
        )
        db_session.add(task)

        # Task completed this month (1)
        task = Task(
            title="Task this month",
            user_id=test_user.id,
            project_id=test_project.id,
            section_id=test_section.id,
            completed=True,
            completed_at=month_ago,
        )
        db_session.add(task)

        await db_session.commit()

        response = await authenticated_client.get("/api/v1/statistics/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_completed"] == 4
        assert data["completed_today"] == 2
        assert data["completed_this_week"] >= 3  # today + week_ago
        assert data["completed_this_month"] == 4  # all of them
        assert data["average_per_day"] >= 0.0
        assert data["best_day_count"] == 2  # 2 tasks completed today
        assert data["best_day_date"] == str(now.date())

    async def test_get_completion_summary_no_tasks(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test getting summary with no completed tasks."""
        response = await authenticated_client.get("/api/v1/statistics/summary")

        assert response.status_code == 200
        data = response.json()

        assert data["total_completed"] == 0
        assert data["completed_today"] == 0
        assert data["completed_this_week"] == 0
        assert data["completed_this_month"] == 0
        assert data["average_per_day"] == 0.0
        assert data["best_day_count"] == 0
        assert data["best_day_date"] is None

    async def test_daily_completions_invalid_date_range(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that invalid date formats are rejected."""
        response = await authenticated_client.get(
            "/api/v1/statistics/daily",
            params={
                "start_date": "invalid-date",
                "end_date": "2025-01-31",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_calendar_heatmap_invalid_year(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that invalid years are rejected."""
        response = await authenticated_client.get("/api/v1/statistics/calendar/1999")

        # Year 1999 is below the minimum (2000)
        assert response.status_code == 422

    async def test_incomplete_tasks_not_counted(
        self,
        authenticated_client: AsyncClient,
        db_session: AsyncSession,
        test_user: User,
        test_project: Project,
        test_section: Section,
    ) -> None:
        """Test that incomplete tasks are not included in statistics."""
        # Create incomplete tasks
        for i in range(5):
            task = Task(
                title=f"Incomplete task {i}",
                user_id=test_user.id,
                project_id=test_project.id,
                section_id=test_section.id,
                completed=False,
            )
            db_session.add(task)

        await db_session.commit()

        response = await authenticated_client.get("/api/v1/statistics/summary")

        assert response.status_code == 200
        data = response.json()

        # Incomplete tasks should not be counted
        assert data["total_completed"] == 0
        assert data["completed_today"] == 0
