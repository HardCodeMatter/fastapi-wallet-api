from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from .config import database_settings


async_engine = create_async_engine(
    url=database_settings.DATABASE_URL_asyncpg, 
    echo=True,
)
async_session_factory = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase): ...


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as async_session:
        yield async_session
