from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from app.core.settings.app_settings import get_app_settings
from app.core.settings.database_settings import DatabaseSettings

db_settings = DatabaseSettings()  # pyright: ignore[reportCallIssue]
app_settings = get_app_settings()

engine = create_async_engine(
    db_settings.connection_url(),
    echo=app_settings.debug,
    pool_pre_ping=True,
)

async_session_local: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session_local() as session:
        yield session
