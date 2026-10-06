import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .repositories import LibraryRepository, MeetingRepository
from .routers import benchmark, bookings, books, experiments, rooms, users
from .settings import settings

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("vitamin-analysis-laboratory")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_ROOT = PROJECT_ROOT / "static"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.library_repository = LibraryRepository()
    application.state.meeting_repository = MeetingRepository()
    logger.info("Application started")
    yield
    logger.info("Application stopped")


app = FastAPI(
    title="Vitamin Analysis Laboratory API",
    version="1.0.0",
    description="Asyncio experiments, validated data and modular FastAPI routing",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_ROOT), name="static")
app.include_router(benchmark.router, prefix=settings.api_prefix)
app.include_router(experiments.router, prefix=settings.api_prefix)
app.include_router(books.router, prefix=settings.api_prefix)
app.include_router(users.router, prefix=settings.api_prefix)
app.include_router(rooms.router, prefix=settings.api_prefix)
app.include_router(bookings.router, prefix=settings.api_prefix)


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_ROOT / "index.html")
