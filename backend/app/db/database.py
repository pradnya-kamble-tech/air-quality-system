"""SQLAlchemy async database engine and session factory.

Uses SQLite by default (zero-config).  Set DATABASE_URL env var to use
PostgreSQL in production, e.g. postgresql+asyncpg://user:pw@host/db.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base for all ORM models."""
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # SQLite-specific: allow same connection from multiple coroutines
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Create all tables if they don't exist."""
    async with engine.begin() as conn:
        # Import models so they register with Base.metadata
        import app.db.models  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Dependency / helper to get an async session."""
    async with async_session() as session:
        yield session
