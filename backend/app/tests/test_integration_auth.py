"""
Integration tests for authentication endpoints.

Tests cover:
- OAuth authentication flow
- Protected endpoint access
- Token validation
- User session management
"""

from httpx import AsyncClient

from app.models.user import User

# pyright: reportAny=false


class TestAuthEndpoints:
    """Test authentication and authorization flows."""

    async def test_google_login_redirects(self, client: AsyncClient) -> None:
        """Test that Google login endpoint returns redirect."""
        response = await client.get("/api/v1/auth/google/login", follow_redirects=False)

        assert response.status_code == 302
        assert "google" in response.headers["location"].lower()

    async def test_access_protected_endpoint_without_token(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint without token returns 307 redirect."""
        response = await client.get("/api/v1/tasks", follow_redirects=False)

        assert response.status_code == 307

    async def test_access_protected_endpoint_with_token(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test accessing protected endpoint with valid token succeeds."""
        response = await authenticated_client.get("/api/v1/tasks")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_access_protected_endpoint_with_invalid_token(self, client: AsyncClient) -> None:
        """Test accessing protected endpoint with invalid token returns 307 redirect."""
        client.cookies.set("access_token", "invalid_token_here")
        response = await client.get("/api/v1/tasks", follow_redirects=False)

        assert response.status_code == 307

    async def test_get_current_user_with_cookie(self, client: AsyncClient, test_user: User, test_user_token: str) -> None:
        """Test getting current authenticated user information using cookie."""
        # Set cookie instead of Authorization header
        client.cookies.set("access_token", test_user_token)

        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "oauth_subject_id" not in data  # Should not expose sensitive OAuth data

    async def test_get_current_user_without_cookie(self, client: AsyncClient) -> None:
        """Test that accessing /me without cookie fails."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    async def test_is_authenticated_with_valid_token(self, client: AsyncClient, test_user_token: str) -> None:
        """Test is_authenticated endpoint with valid token."""
        client.cookies.set("access_token", test_user_token)

        response = await client.get("/api/v1/auth/is_authenticated")

        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is True

    async def test_is_authenticated_without_token(self, client: AsyncClient) -> None:
        """Test is_authenticated endpoint without token."""
        response = await client.get("/api/v1/auth/is_authenticated")

        assert response.status_code == 200
        data = response.json()
        assert data["is_authenticated"] is False

    async def test_logout(self, client: AsyncClient, test_user_token: str) -> None:
        """Test logout clears the access token cookie."""
        client.cookies.set("access_token", test_user_token)

        response = await client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert "logged out" in data["message"].lower()


class TestAuthSecurity:
    """Test authentication security and edge cases."""

    async def test_malformed_token(self, client: AsyncClient) -> None:
        """Test that malformed JWT token is rejected."""
        client.cookies.set("access_token", "not.a.valid.jwt.token.at.all")
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_token_with_invalid_signature(self, client: AsyncClient) -> None:
        """Test that token with tampered signature is rejected."""
        # This is a valid JWT structure but with wrong signature
        tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        client.cookies.set("access_token", tampered_token)
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_empty_token(self, client: AsyncClient) -> None:
        """Test that empty token is rejected."""
        client.cookies.set("access_token", "")
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_whitespace_only_token(self, client: AsyncClient) -> None:
        """Test that whitespace-only token is rejected."""
        client.cookies.set("access_token", "   ")
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_sql_injection_in_auth(self, client: AsyncClient) -> None:
        """Test that SQL injection attempts in token are safely handled."""
        malicious_token = "' OR '1'='1"
        client.cookies.set("access_token", malicious_token)
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_multiple_consecutive_auth_failures(self, client: AsyncClient) -> None:
        """Test that multiple failed auth attempts are handled gracefully."""
        client.cookies.set("access_token", "invalid_token")

        for _ in range(5):
            response = await client.get("/api/v1/auth/me")
            assert response.status_code == 401

    async def test_very_long_token(self, client: AsyncClient) -> None:
        """Test that extremely long token is rejected gracefully."""
        long_token = "A" * 10000
        client.cookies.set("access_token", long_token)
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401

    async def test_token_with_special_characters(self, client: AsyncClient) -> None:
        """Test tokens with special characters are handled safely."""
        special_chars_token = "token<>?/\\|!@#$%^&*()"
        client.cookies.set("access_token", special_chars_token)
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
