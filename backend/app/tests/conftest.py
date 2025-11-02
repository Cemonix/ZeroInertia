"""
Pytest configuration and fixtures for integration tests.

This module provides shared fixtures for testing, including:
- Test database setup/teardown
- Test client for API calls
- Authentication helpers
- Database session management
"""

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import get_db
from app.core.settings.database_settings import DatabaseSettings
from app.main import app
from app.models import Project, Section, Task
from app.models.base import Base
from app.models.user import User
from app.services.jwt_service import JWTService

TEST_DB_SETTINGS = DatabaseSettings()  # pyright: ignore[reportCallIssue]
TEST_DB_SETTINGS.database_name = "zeroinertia_test"

# Create test database engine with optimized settings for testing
test_engine = create_async_engine(
    TEST_DB_SETTINGS.connection_url(),
    echo=False,  # Set to True for SQL debugging
    pool_pre_ping=True,
    poolclass=NullPool,  # Use NullPool for testing to avoid connection pool issues
)

# Create test session factory
TestSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_database() -> AsyncGenerator[None, None]:
    """
    Create test database tables before each test and drop them after.

    This ensures complete isolation between tests.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP client for testing API endpoints.

    This client uses the test database session instead of the production one.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Enable cookie handling and follow redirects for the test client
    async with AsyncClient(
        transport=ASGITransport(app=app),  # type: ignore
        base_url="http://test",
        follow_redirects=True,  # Follow redirects (like trailing slash redirects)
        cookies={},  # Initialize with empty cookies dict to enable cookie jar
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Create a test user in the database (OAuth-based).

    Returns:
        User: A test user with OAuth credentials
    """
    user = User(
        email="test@example.com",
        oauth_provider="google",
        oauth_subject_id="test_oauth_id_123",
        full_name="Test User",
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
async def test_user_token(test_user: User) -> str:
    """
    Create an access token for the test user.

    Returns:
        str: JWT access token
    """
    return JWTService.create_access_token(user_id=test_user.id, email=test_user.email)


@pytest.fixture
async def authenticated_client(client: AsyncClient, test_user_token: str) -> AsyncClient:
    """
    Provide an authenticated HTTP client with JWT token in cookie.

    This client includes the access_token cookie in all requests.
    """
    client.cookies.set("access_token", test_user_token)
    return client


@pytest.fixture
def auth_headers(test_user_token: str) -> dict[str, str]:
    """
    Provide authentication headers for manual requests.

    Returns:
        dict: Headers with Authorization token
    """
    return {"Authorization": f"Bearer {test_user_token}"}


# Helper fixtures for common test data


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        title="Test Project",
        user_id=test_user.id,
        order_index=0,
    )

    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    return project


@pytest.fixture
async def test_section(db_session: AsyncSession, test_user: User, test_project: Project) -> Section:
    """Create a test section."""
    section = Section(
        title="Test Section",
        project_id=test_project.id,
        user_id=test_user.id,
        order_index=0,
    )

    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)

    return section


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: User, test_project: Project, test_section: Section) -> Task:
    """Create a test task."""
    task = Task(
        title="Test Task",
        description="A test task",
        user_id=test_user.id,
        project_id=test_project.id,
        section_id=test_section.id,
        order_index=0,
        completed=False,
        archived=False,
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return task
