"""Unit tests for recurrence calculation logic."""
import calendar
from datetime import datetime, timezone

from app.services.task_service import (
    _calculate_next_due_date,  # pyright: ignore[reportPrivateUsage]
)


class TestCalculateNextDueDate:
    """Test suite for _calculate_next_due_date function."""

    def test_daily_recurrence(self):
        """Test daily recurrence (every N days)."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 1, "days", None)
        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 3, "days", None)
        assert result == datetime(2024, 1, 18, 10, 0, 0, tzinfo=timezone.utc)

    def test_weekly_recurrence_without_specific_days(self):
        """Test weekly recurrence without specific days (every N weeks)."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)  # Monday

        result = _calculate_next_due_date(base_date, 1, "weeks", None)
        assert result == datetime(2024, 1, 22, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 2, "weeks", None)
        assert result == datetime(2024, 1, 29, 10, 0, 0, tzinfo=timezone.utc)

    def test_weekly_recurrence_with_specific_days(self):
        """Test weekly recurrence on specific weekdays."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)  # Monday (0)

        # Next Wednesday (2) should be Jan 17
        result = _calculate_next_due_date(base_date, 1, "weeks", [2])
        assert result == datetime(2024, 1, 17, 10, 0, 0, tzinfo=timezone.utc)

        # On Monday, next Monday (same weekday) should be next week
        result = _calculate_next_due_date(base_date, 1, "weeks", [0])
        assert result == datetime(2024, 1, 22, 10, 0, 0, tzinfo=timezone.utc)

        # Multiple days: next occurrence should be nearest future day
        result = _calculate_next_due_date(base_date, 1, "weeks", [2, 4])  # Wed, Fri
        assert result == datetime(2024, 1, 17, 10, 0, 0, tzinfo=timezone.utc)  # Wednesday

    def test_weekly_recurrence_every_two_weeks_with_days(self):
        """Test every 2 weeks on specific days."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)  # Monday

        # Every 2 weeks on Monday - should jump to 2 weeks later
        result = _calculate_next_due_date(base_date, 2, "weeks", [0])
        assert result == datetime(2024, 1, 29, 10, 0, 0, tzinfo=timezone.utc)

        # Every 2 weeks on Wednesday - should be this Wednesday first
        result = _calculate_next_due_date(base_date, 2, "weeks", [2])
        assert result == datetime(2024, 1, 17, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_recurrence_simple(self):
        """Test monthly recurrence on same day."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 1, "months", None)
        assert result == datetime(2024, 2, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 3, "months", None)
        assert result == datetime(2024, 4, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_recurrence_year_boundary(self):
        """Test monthly recurrence crossing year boundary."""
        base_date = datetime(2024, 11, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 2, "months", None)
        assert result == datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 3, "months", None)
        assert result == datetime(2025, 2, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_monthly_recurrence_day_overflow(self):
        """Test monthly recurrence when day doesn't exist in target month."""
        # Jan 31 -> Feb should become Feb 28/29
        base_date = datetime(2024, 1, 31, 10, 0, 0, tzinfo=timezone.utc)
        result = _calculate_next_due_date(base_date, 1, "months", None)
        assert result == datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)  # 2024 is leap year

        # Jan 31 -> April (30 days) should become Apr 30
        result = _calculate_next_due_date(base_date, 3, "months", None)
        assert result == datetime(2024, 4, 30, 10, 0, 0, tzinfo=timezone.utc)

        # Non-leap year: Jan 31 2023 -> Feb should be Feb 28
        base_date = datetime(2023, 1, 31, 10, 0, 0, tzinfo=timezone.utc)
        result = _calculate_next_due_date(base_date, 1, "months", None)
        assert result == datetime(2023, 2, 28, 10, 0, 0, tzinfo=timezone.utc)

    def test_yearly_recurrence(self):
        """Test yearly recurrence."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 1, "years", None)
        assert result == datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        result = _calculate_next_due_date(base_date, 2, "years", None)
        assert result == datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_yearly_recurrence_leap_year_feb_29(self):
        """Test yearly recurrence on Feb 29 (leap year edge case)."""
        # Feb 29 2024 (leap year) -> 2025 (non-leap) should become Feb 28
        base_date = datetime(2024, 2, 29, 10, 0, 0, tzinfo=timezone.utc)
        result = _calculate_next_due_date(base_date, 1, "years", None)
        assert result == datetime(2025, 2, 28, 10, 0, 0, tzinfo=timezone.utc)

        # Feb 29 2024 -> 2028 (leap year) should stay Feb 29
        result = _calculate_next_due_date(base_date, 4, "years", None)
        assert result == datetime(2028, 2, 29, 10, 0, 0, tzinfo=timezone.utc)

    def test_invalid_recurrence_returns_default(self):
        """Test that invalid/missing recurrence params return default (next day)."""
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        # Missing interval
        result = _calculate_next_due_date(base_date, None, "days", None)
        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)

        # Missing unit
        result = _calculate_next_due_date(base_date, 1, None, None)
        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)

        # Both missing
        result = _calculate_next_due_date(base_date, None, None, None)
        assert result == datetime(2024, 1, 16, 10, 0, 0, tzinfo=timezone.utc)

    def test_none_current_due_uses_now(self):
        """Test that None current_due uses current time."""
        result = _calculate_next_due_date(None, 1, "days", None)
        now = datetime.now(timezone.utc)

        # Result should be approximately 1 day from now
        diff = (result - now).total_seconds()
        assert 86390 < diff < 86410  # ~24 hours (with small tolerance)

    def test_leap_year_detection(self):
        """Test that leap year is correctly detected using calendar.isleap."""
        # 2024 is a leap year
        assert calendar.isleap(2024)

        # 2023 is not
        assert not calendar.isleap(2023)

        # 2000 is (divisible by 400)
        assert calendar.isleap(2000)

        # 1900 is not (divisible by 100 but not 400)
        assert not calendar.isleap(1900)

    def test_complex_scenario_every_3_months(self):
        """Test real-world scenario: task due every 3 months."""
        # Start on Jan 15
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

        # First recurrence: Apr 15
        next_date = _calculate_next_due_date(base_date, 3, "months", None)
        assert next_date == datetime(2024, 4, 15, 10, 0, 0, tzinfo=timezone.utc)

        # Second recurrence: Jul 15
        next_date = _calculate_next_due_date(next_date, 3, "months", None)
        assert next_date == datetime(2024, 7, 15, 10, 0, 0, tzinfo=timezone.utc)

        # Third recurrence: Oct 15
        next_date = _calculate_next_due_date(next_date, 3, "months", None)
        assert next_date == datetime(2024, 10, 15, 10, 0, 0, tzinfo=timezone.utc)

        # Fourth recurrence: Jan 15, 2025
        next_date = _calculate_next_due_date(next_date, 3, "months", None)
        assert next_date == datetime(2025, 1, 15, 10, 0, 0, tzinfo=timezone.utc)

    def test_complex_scenario_every_2_weeks_mon_wed_fri(self):
        """Test real-world scenario: every 2 weeks on Mon/Wed/Fri."""
        # Start on Monday Jan 15, 2024
        base_date = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        days = [0, 2, 4]  # Mon, Wed, Fri

        # From Monday, next should be Wednesday (same week)
        next_date = _calculate_next_due_date(base_date, 2, "weeks", days)
        assert next_date == datetime(2024, 1, 17, 10, 0, 0, tzinfo=timezone.utc)  # Wednesday

        # From Wednesday, next should be Friday (same week)
        next_date = _calculate_next_due_date(next_date, 2, "weeks", days)
        assert next_date == datetime(2024, 1, 19, 10, 0, 0, tzinfo=timezone.utc)  # Friday

        # From Friday, next should be Monday in 2 weeks (Jan 29)
        next_date = _calculate_next_due_date(next_date, 2, "weeks", days)
        assert next_date == datetime(2024, 1, 29, 10, 0, 0, tzinfo=timezone.utc)  # Monday 2 weeks later
