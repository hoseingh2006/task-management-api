from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

DB_URL = URL.create(
    "postgresql+asyncpg",
    settings.database_user,
    settings.database_password,
    settings.database_host,
    settings.database_port,
    settings.database_name,
)
DB_ENGIN = create_async_engine(DB_URL, echo=True)
LocalSession = async_sessionmaker(DB_ENGIN, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
