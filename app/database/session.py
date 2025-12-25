from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from sqlalchemy.orm import DeclarativeBase
from app.config.settings import get_settings
from sqlalchemy.ext.asyncio import AsyncEngine

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass


async def init_db(engine: AsyncEngine):
    async with engine.connect() as conn:
        await conn.begin()
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
