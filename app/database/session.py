from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Engine is created once at startup; echo=True logs SQL in debug mode
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,   # drops stale connections before use
)

# Factory that produces AsyncSession objects on demand
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields a session and guarantees cleanup."""
    async with AsyncSessionLocal() as session:
        yield session
