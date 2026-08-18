from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm.exc import DeclarativeBase
from core.config import settings

URL = URL.create(
    "postgresql+asyncpg",
    settings.database_user,
    settings.database_password,
    settings.database_host,
    settings.database_port,
    settings.database_name,
)
ENGIN = create_async_engine(URL, echo=True)
LocalSession = async_sessionmaker(ENGIN, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
