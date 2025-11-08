"""
Integration tests for push notification endpoints.

Tests cover:
- Push subscription management (subscribe, unsubscribe, get subscriptions)
- Token validation and error handling
- Multi-device subscription support
- FCM token format validation
- Authorization and authentication
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from firebase_admin import exceptions as firebase_exceptions
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.push_subscription import PushSubscription
from app.models.user import User

# pyright: reportAny=false, reportPrivateUsage=false


class TestNotificationEndpoints:
    """Test push notification subscription endpoints."""

    async def test_subscribe_creates_new_subscription(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test creating a new push subscription."""
        subscription_data = {
            "endpoint": "test_fcm_token_12345",
            "user_agent": "Mozilla/5.0 (Test Browser)",
        }

        response = await authenticated_client.post(
            "/api/v1/notifications/subscribe", json=subscription_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["endpoint"] == subscription_data["endpoint"]
        assert data["user_agent"] == subscription_data["user_agent"]
        assert data["user_id"] == str(test_user.id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify subscription was created in database
        result = await db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == test_user.id)
        )
        subscription = result.scalar_one()
        assert subscription.endpoint == subscription_data["endpoint"]

    async def test_subscribe_updates_existing_subscription(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that subscribing with same endpoint updates existing subscription."""
        endpoint = "test_fcm_token_existing"

        # Create initial subscription
        initial_subscription = PushSubscription(
            user_id=test_user.id, endpoint=endpoint, user_agent="Old Browser"
        )
        db_session.add(initial_subscription)
        await db_session.commit()
        await db_session.refresh(initial_subscription)

        # Subscribe again with same endpoint but different user_agent
        subscription_data = {
            "endpoint": endpoint,
            "user_agent": "New Browser",
        }

        response = await authenticated_client.post(
            "/api/v1/notifications/subscribe", json=subscription_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(initial_subscription.id)  # Same subscription ID
        assert data["user_agent"] == "New Browser"  # Updated user agent

        # Verify only one subscription exists
        result = await db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == test_user.id)
        )
        subscriptions = result.scalars().all()
        assert len(subscriptions) == 1

    async def test_subscribe_without_authentication(self, client: AsyncClient) -> None:
        """Test that subscribing without authentication fails."""
        subscription_data = {
            "endpoint": "test_fcm_token_12345",
            "user_agent": "Mozilla/5.0 (Test Browser)",
        }

        response = await client.post("/api/v1/notifications/subscribe", json=subscription_data)

        assert response.status_code == 401

    async def test_get_subscriptions(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test getting all user subscriptions."""
        # Create multiple subscriptions
        subscriptions = [
            PushSubscription(user_id=test_user.id, endpoint=f"token_{i}", user_agent=f"Browser {i}")
            for i in range(3)
        ]
        db_session.add_all(subscriptions)
        await db_session.commit()

        response = await authenticated_client.get("/api/v1/notifications/subscriptions")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("endpoint" in sub for sub in data)
        assert all("user_agent" in sub for sub in data)

    async def test_get_subscriptions_empty(self, authenticated_client: AsyncClient) -> None:
        """Test getting subscriptions when user has none."""
        response = await authenticated_client.get("/api/v1/notifications/subscriptions")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    async def test_unsubscribe_existing_subscription(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test unsubscribing from push notifications."""
        endpoint = "test_fcm_token_to_delete"

        # Create subscription
        subscription = PushSubscription(user_id=test_user.id, endpoint=endpoint)
        db_session.add(subscription)
        await db_session.commit()

        # Unsubscribe
        response = await authenticated_client.post(
            "/api/v1/notifications/unsubscribe", json={"endpoint": endpoint}
        )

        assert response.status_code == 204

        # Verify subscription was deleted
        result = await db_session.execute(
            select(PushSubscription).where(
                PushSubscription.user_id == test_user.id,
                PushSubscription.endpoint == endpoint,
            )
        )
        assert result.scalar_one_or_none() is None

    async def test_unsubscribe_nonexistent_subscription(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test unsubscribing from a subscription that doesn't exist."""
        response = await authenticated_client.post(
            "/api/v1/notifications/unsubscribe", json={"endpoint": "nonexistent_token"}
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_all_subscriptions(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test deleting all user subscriptions."""
        # Create multiple subscriptions
        subscriptions = [
            PushSubscription(user_id=test_user.id, endpoint=f"token_{i}") for i in range(3)
        ]
        db_session.add_all(subscriptions)
        await db_session.commit()

        response = await authenticated_client.delete("/api/v1/notifications/subscriptions/all")

        assert response.status_code == 204

        # Verify all subscriptions were deleted
        result = await db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == test_user.id)
        )
        assert result.scalars().all() == []

    async def test_delete_all_subscriptions_when_none_exist(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test deleting all subscriptions when user has none."""
        response = await authenticated_client.delete("/api/v1/notifications/subscriptions/all")

        assert response.status_code == 204  # Should succeed even with no subscriptions

    async def test_subscribe_with_optional_user_agent(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test subscribing without user_agent (optional field)."""
        subscription_data = {
            "endpoint": "test_fcm_token_no_agent",
            # user_agent is optional
        }

        response = await authenticated_client.post(
            "/api/v1/notifications/subscribe", json=subscription_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_agent"] is None

    async def test_multiple_users_can_have_different_subscriptions(
        self, db_session: AsyncSession
    ) -> None:
        """Test that different users can have independent subscriptions."""
        # Create two users
        user1 = User(
            email="user1@example.com",
            oauth_provider="google",
            oauth_subject_id="user1_oauth_id",
            full_name="User One",
        )
        user2 = User(
            email="user2@example.com",
            oauth_provider="google",
            oauth_subject_id="user2_oauth_id",
            full_name="User Two",
        )
        db_session.add_all([user1, user2])
        await db_session.commit()
        await db_session.refresh(user1)
        await db_session.refresh(user2)

        # Create subscriptions for both users
        sub1 = PushSubscription(user_id=user1.id, endpoint="token_user1")
        sub2 = PushSubscription(user_id=user2.id, endpoint="token_user2")
        db_session.add_all([sub1, sub2])
        await db_session.commit()

        # Verify each user has their own subscription
        result1 = await db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == user1.id)
        )
        assert len(result1.scalars().all()) == 1

        result2 = await db_session.execute(
            select(PushSubscription).where(PushSubscription.user_id == user2.id)
        )
        assert len(result2.scalars().all()) == 1


class TestNotificationService:
    """Test push notification service functionality."""

    @pytest.fixture
    def mock_firebase(self):
        """Mock Firebase Admin SDK."""
        with patch("app.services.notification_service.firebase_admin") as mock_fb, patch(
            "app.services.notification_service.messaging"
        ) as mock_msg:
            # Mock initialization
            mock_app = MagicMock()
            mock_fb.initialize_app.return_value = mock_app

            # Mock credentials
            with patch("app.services.notification_service.credentials") as mock_cred:
                mock_cred.Certificate.return_value = MagicMock()
                yield mock_fb, mock_msg, mock_cred

    @pytest.fixture
    async def test_subscription(
        self, db_session: AsyncSession, test_user: User
    ) -> PushSubscription:
        """Create a test push subscription."""
        subscription = PushSubscription(
            user_id=test_user.id, endpoint="test_fcm_token_for_service"
        )
        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)
        return subscription

    async def test_send_notification_to_user_success(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test sending notification to a user with valid subscription."""
        from app.services import notification_service

        with patch.object(
            notification_service, "send_push_notification", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = (True, None)  # Success

            count = await notification_service.send_notification_to_user(
                db=db_session, user_id=test_user.id, title="Test", body="Test notification"
            )

            assert count == 1
            mock_send.assert_called_once()

    async def test_send_notification_to_user_no_subscriptions(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test sending notification to user with no subscriptions."""
        from app.services import notification_service

        count = await notification_service.send_notification_to_user(
            db=db_session, user_id=test_user.id, title="Test", body="Test notification"
        )

        assert count == 0

    async def test_send_notification_cleans_up_invalid_tokens(
        self, db_session: AsyncSession, test_user: User, test_subscription: PushSubscription
    ) -> None:
        """Test that invalid FCM tokens are cleaned up automatically."""
        from app.services import notification_service

        with patch.object(
            notification_service, "send_push_notification", new_callable=AsyncMock
        ) as mock_send:
            # Simulate invalid token error
            mock_send.return_value = (False, "invalid_token")

            count = await notification_service.send_notification_to_user(
                db=db_session, user_id=test_user.id, title="Test", body="Test notification"
            )

            assert count == 0

            # Verify subscription was deleted
            result = await db_session.execute(
                select(PushSubscription).where(PushSubscription.id == test_subscription.id)
            )
            assert result.scalar_one_or_none() is None

    async def test_send_task_reminder(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test sending task reminder notification."""
        from app.services import notification_service

        task_id = uuid4()

        with patch.object(
            notification_service, "send_push_notification", new_callable=AsyncMock
        ) as mock_send:
            mock_send.return_value = (True, None)

            count = await notification_service.send_task_reminder(
                db=db_session,
                user_id=test_user.id,
                task_title="Complete project",
                task_id=task_id,
                due_datetime="in 15 minutes",
            )

            assert count == 1
            mock_send.assert_called_once()
            # Verify the call was made with correct arguments
            call_args = mock_send.call_args[0]  # Get positional args
            title_arg = call_args[1]
            body_arg = call_args[2]
            data_arg = call_args[3] if len(call_args) > 3 else None

            assert title_arg == "Task Reminder"
            assert "Complete project" in body_arg
            assert data_arg is not None
            assert data_arg["task_id"] == str(task_id)
            assert data_arg["type"] == "task_reminder"

    async def test_send_notification_with_retry_on_transient_error(
        self, test_subscription: PushSubscription
    ) -> None:
        """Test that transient FCM errors trigger retry logic."""
        from app.services import notification_service

        with patch("app.services.notification_service.asyncio.to_thread") as mock_to_thread:
            # First call fails with transient error, second succeeds
            error = firebase_exceptions.FirebaseError(
                code="unavailable", message="Service temporarily unavailable"
            )
            mock_to_thread.side_effect = [error, "success_message_id"]

            with patch("app.services.notification_service.asyncio.sleep", new_callable=AsyncMock):
                success, error_code = await notification_service._send_push_notification_with_retry(
                    subscription=test_subscription,
                    title="Test",
                    body="Test body",
                    frontend_url="http://localhost:5173",
                )

            # Should succeed after retry
            assert success is True
            assert error_code is None
            assert mock_to_thread.call_count == 2

    async def test_send_notification_fails_after_max_retries(
        self, test_subscription: PushSubscription
    ) -> None:
        """Test that notification fails after max retries."""
        from app.services import notification_service

        with patch("app.services.notification_service.asyncio.to_thread") as mock_to_thread:
            # All attempts fail
            error = firebase_exceptions.FirebaseError(
                code="unavailable", message="Service temporarily unavailable"
            )
            mock_to_thread.side_effect = error

            with patch("app.services.notification_service.asyncio.sleep", new_callable=AsyncMock):
                success, error_code = await notification_service._send_push_notification_with_retry(
                    subscription=test_subscription,
                    title="Test",
                    body="Test body",
                    frontend_url="http://localhost:5173",
                    attempt=1,
                )

            # Should fail after retries
            assert success is False
            assert error_code == "unavailable"
            assert mock_to_thread.call_count == 3  # Initial + 2 retries (MAX_RETRIES = 3)

    async def test_send_notification_invalid_token_no_retry(
        self, test_subscription: PushSubscription
    ) -> None:
        """Test that invalid token errors don't trigger retry."""
        from app.services import notification_service

        with patch("app.services.notification_service.asyncio.to_thread") as mock_to_thread:
            # Simulate invalid token
            error = firebase_exceptions.FirebaseError(
                code="invalid-registration-token", message="Invalid token"
            )
            mock_to_thread.side_effect = error

            success, error_code = await notification_service._send_push_notification_with_retry(
                subscription=test_subscription,
                title="Test",
                body="Test body",
                frontend_url="http://localhost:5173",
            )

            # Should fail immediately without retry
            assert success is False
            assert error_code == "invalid_token"
            assert mock_to_thread.call_count == 1  # No retry


class TestPushSubscriptionModel:
    """Test PushSubscription model."""

    async def test_create_subscription_with_all_fields(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test creating subscription with all fields."""
        subscription = PushSubscription(
            user_id=test_user.id, endpoint="test_token", user_agent="Test Browser"
        )

        db_session.add(subscription)
        await db_session.commit()
        await db_session.refresh(subscription)

        assert subscription.id is not None
        assert subscription.user_id == test_user.id
        assert subscription.endpoint == "test_token"
        assert subscription.user_agent == "Test Browser"
        assert subscription.created_at is not None
        assert subscription.updated_at is not None

    async def test_subscription_unique_endpoint(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that endpoints must be unique."""
        endpoint = "unique_test_token"

        sub1 = PushSubscription(user_id=test_user.id, endpoint=endpoint)
        db_session.add(sub1)
        await db_session.commit()

        # Try to create another subscription with same endpoint
        sub2 = PushSubscription(user_id=test_user.id, endpoint=endpoint)
        db_session.add(sub2)

        with pytest.raises(Exception):  # IntegrityError due to unique constraint  # noqa: B017
            await db_session.commit()

    async def test_subscription_cascade_delete_with_user(
        self, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test that subscriptions are deleted when user is deleted."""
        subscription = PushSubscription(user_id=test_user.id, endpoint="cascade_test_token")
        db_session.add(subscription)
        await db_session.commit()

        # Delete user
        await db_session.delete(test_user)
        await db_session.commit()

        # Verify subscription was also deleted
        result = await db_session.execute(
            select(PushSubscription).where(PushSubscription.endpoint == "cascade_test_token")
        )
        assert result.scalar_one_or_none() is None
