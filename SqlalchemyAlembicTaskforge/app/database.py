from collections.abc import AsyncIterator
from typing import Annotated, Any, cast

from fastapi import Depends, Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def engine_options(database_url: str) -> dict[str, Any]:
    options: dict[str, Any] = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "echo": False,
    }
    if database_url.startswith("postgresql+"):
        options.update(pool_size=10, max_overflow=20)
    return options


class Database:
    def __init__(self, database_url: str) -> None:
        self.engine: AsyncEngine = create_async_engine(
            database_url,
            **engine_options(database_url),
        )
        if self.engine.dialect.name == "sqlite":
            event.listen(self.engine.sync_engine, "connect", enable_sqlite_foreign_keys)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        await self.engine.dispose()


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    database = cast(Database, request.app.state.database)
    async with database.session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


DatabaseSession = Annotated[AsyncSession, Depends(get_db, scope="function")]


def enable_sqlite_foreign_keys(connection: Any, record: Any) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
