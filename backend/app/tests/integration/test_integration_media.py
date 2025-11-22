"""
Integration tests for media endpoints.

Tests cover:
- Media CRUD operations (books, games, movies, shows, manga, anime)
- Duplicate title checking (scoped to media type)
- Status filtering
- Yearly statistics
- User isolation
"""

from datetime import datetime

from httpx import AsyncClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.models.media import Anime, Book, Game, Manga, Movie, Show
from app.models.user import User

# pyright: reportAny=false


class TestMediaDuplicateCheck:
    """Test duplicate title checking functionality (scoped to media type)."""

    async def test_duplicate_check_with_no_matches(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test duplicate check when no matching titles exist for the media type."""
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Nonexistent Title", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    async def test_duplicate_check_returns_list(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test that duplicate check returns a list."""
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Test", "media_type": "game"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_duplicate_check_finds_exact_match_book(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check finds exact matching book title."""
        book = Book(
            title="The Great Gatsby",
            creator="F. Scott Fitzgerald",
            status="completed",
            user_id=test_user.id,
        )
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "The Great Gatsby", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "The Great Gatsby"
        assert data[0]["status"] == "completed"
        assert data[0]["id"] == str(book.id)

    async def test_duplicate_check_finds_partial_match(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check finds partial matching titles."""
        book = Book(
            title="Harry Potter and the Philosopher's Stone",
            creator="J.K. Rowling",
            status="completed",
            user_id=test_user.id,
        )
        db_session.add(book)
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Harry Potter", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Harry Potter" in data[0]["title"]

    async def test_duplicate_check_case_insensitive(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check is case insensitive."""
        book = Book(
            title="The Lord of the Rings",
            creator="J.R.R. Tolkien",
            status="completed",
            user_id=test_user.id,
        )
        db_session.add(book)
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "lord of the rings", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "The Lord of the Rings"

    async def test_duplicate_check_scoped_to_media_type(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check only returns matches for the specified media type."""
        book = Book(
            title="The Witcher",
            creator="Andrzej Sapkowski",
            status="completed",
            user_id=test_user.id,
        )
        game = Game(
            title="The Witcher 3",
            status="completed",
            platform="PC",
            user_id=test_user.id,
        )
        show = Show(
            title="The Witcher",
            status="in_progress",
            user_id=test_user.id,
        )

        db_session.add_all([book, game, show])
        await db_session.commit()

        # Check books - should only return the book
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Witcher", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "The Witcher"

        # Check games - should only return the game
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Witcher", "media_type": "game"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "The Witcher 3"

        # Check shows - should only return the show
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Witcher", "media_type": "show"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "The Witcher"

    async def test_duplicate_check_includes_completion_date(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check includes completion date for completed media."""
        completion_date = datetime(2024, 1, 15)
        game = Game(
            title="Elden Ring",
            status="completed",
            platform="PS5",
            user_id=test_user.id,
            completed_at=completion_date,
        )
        db_session.add(game)
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Elden Ring", "media_type": "game"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["completed_at"] is not None
        assert "2024-01-15" in data[0]["completed_at"]

    async def test_duplicate_check_user_isolation(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check only returns current user's media."""
        # Create media for test user
        test_book = Book(
            title="User Book",
            creator="Author",
            status="completed",
            user_id=test_user.id,
        )

        # Create another user and their media
        other_user = User(
            email="other@example.com",
            oauth_provider="google",
            oauth_subject_id="other_oauth_id",
            full_name="Other User",
        )
        db_session.add(other_user)
        await db_session.commit()
        await db_session.refresh(other_user)

        other_book = Book(
            title="User Book",
            creator="Different Author",
            status="completed",
            user_id=other_user.id,
        )

        db_session.add_all([test_book, other_book])
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "User Book", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        # Should only return test user's book
        assert len(data) == 1
        assert data[0]["id"] == str(test_book.id)

    async def test_duplicate_check_requires_authentication(
        self, client: AsyncClient
    ) -> None:
        """Test duplicate check requires authentication."""
        response = await client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Test", "media_type": "book"},
        )

        assert response.status_code == 401

    async def test_duplicate_check_requires_title_parameter(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test duplicate check requires title parameter."""
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"media_type": "book"},
        )

        assert response.status_code == 422  # Validation error

    async def test_duplicate_check_requires_media_type_parameter(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test duplicate check requires media_type parameter."""
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Test"},
        )

        assert response.status_code == 422  # Validation error

    async def test_duplicate_check_with_multiple_matches_same_type(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check returns multiple matches of same type."""
        movie1 = Movie(
            title="Spider-Man",
            status="completed",
            user_id=test_user.id,
        )
        movie2 = Movie(
            title="Spider-Man: Homecoming",
            status="planned",
            user_id=test_user.id,
        )
        movie3 = Movie(
            title="The Amazing Spider-Man",
            status="completed",
            user_id=test_user.id,
        )

        db_session.add_all([movie1, movie2, movie3])
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Spider-Man", "media_type": "movie"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        titles = [m["title"] for m in data]
        assert "Spider-Man" in titles
        assert "Spider-Man: Homecoming" in titles
        assert "The Amazing Spider-Man" in titles

    async def test_duplicate_check_includes_item_itself_when_editing(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check includes the item itself (filtering happens in frontend)."""
        book = Book(
            title="Existing Book Title",
            creator="Author Name",
            status="completed",
            user_id=test_user.id,
        )
        db_session.add(book)
        await db_session.commit()
        await db_session.refresh(book)

        # When editing this book, searching for its own title should return itself
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Existing Book Title", "media_type": "book"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(book.id)
        assert data[0]["title"] == "Existing Book Title"
        # Frontend is responsible for filtering out the current item when editing

    async def test_duplicate_check_manga_type(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check works for manga media type."""
        manga = Manga(
            title="One Piece",
            author="Eiichiro Oda",
            status="in_progress",
            user_id=test_user.id,
        )
        db_session.add(manga)
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "One Piece", "media_type": "manga"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "One Piece"

    async def test_duplicate_check_anime_type(
        self, authenticated_client: AsyncClient, db_session: AsyncSession, test_user: User
    ) -> None:
        """Test duplicate check works for anime media type."""
        anime = Anime(
            title="Attack on Titan",
            episodes=75,
            status="completed",
            user_id=test_user.id,
        )
        db_session.add(anime)
        await db_session.commit()

        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Attack on Titan", "media_type": "anime"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Attack on Titan"

    async def test_duplicate_check_invalid_media_type(
        self, authenticated_client: AsyncClient
    ) -> None:
        """Test duplicate check rejects invalid media types."""
        response = await authenticated_client.get(
            "/api/v1/media/duplicate-check",
            params={"title": "Test", "media_type": "invalid_type"},
        )

        assert response.status_code == 422  # Validation error
