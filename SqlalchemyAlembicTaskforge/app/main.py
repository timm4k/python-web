from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Database
from app.routers import tags, tasks, users
from app.settings import Settings, require_database_url

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


def create_app(database_url: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        database = Database(database_url or require_database_url())
        application.state.database = database
        print("[DATABASE] Music workflow session factory ready")
        try:
            yield
        finally:
            await database.dispose()
            print("[DATABASE] Music workflow connections closed")

    application = FastAPI(
        title="Music Workflow API",
        description="Async SQLAlchemy relationships, CRUD and Alembic evolution",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @application.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    application.include_router(users.router)
    application.include_router(tags.router)
    application.include_router(tasks.router)
    return application


app = create_app()


def run() -> None:
    settings = Settings.from_environment()
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
