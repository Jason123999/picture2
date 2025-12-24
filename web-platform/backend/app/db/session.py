from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings

_settings = get_settings()

async_engine = create_async_engine(
    _settings.database_url,
    future=True,
    echo=False,
)

async_session = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield database session for request scope."""

    async with async_session() as session:  # type: ignore[call-arg]
        yield session
