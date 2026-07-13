<<<<<<< HEAD
"""SQLAlchemy 2.0 async engine with production connection pooling."""
=======
"""
AFM Database — SQLAlchemy 2.0 async with connection pooling
"""
>>>>>>> origin_afm/main

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from config.config import get_settings

settings = get_settings()

<<<<<<< HEAD
engine = create_async_engine(
    settings.database_url,
=======
_connect_args = {"ssl": True} if settings.db_ssl_required else {}

engine = create_async_engine(
    settings.resolved_database_url,
>>>>>>> origin_afm/main
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.is_development,
<<<<<<< HEAD
=======
    connect_args=_connect_args,
>>>>>>> origin_afm/main
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
