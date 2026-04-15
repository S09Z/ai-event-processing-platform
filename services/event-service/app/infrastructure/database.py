"""Async SQLAlchemy database engine and session factory."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.APP_ENV == "development",
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """
    FastAPI dependency that yields an async database session.

    Usage:
        @router.get("/events")
        async def list_events(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    async with AsyncSessionFactory() as session:
        yield session
