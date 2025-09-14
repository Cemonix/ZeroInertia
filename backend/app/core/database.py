from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker

from app.core.settings.database_settings import DatabaseSettings

db_settings = DatabaseSettings()  # pyright: ignore[reportCallIssue]

engine = create_async_engine(
    db_settings.connection_url(),
    echo=True,  # TODO: Set to False in production
    pool_pre_ping=True,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
