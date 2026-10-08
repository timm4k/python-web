from collections import deque
from collections.abc import AsyncIterator, Callable
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from copy import deepcopy
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.dependencies import log_user_agent
from app.errors import (
    LinkNotFoundError,
    link_not_found_handler,
    validation_error_handler,
)
from app.middleware import SimpleRateLimiter, create_tracing_middleware
from app.repositories import (
    USER_SEED,
    LinkRepository,
    NotesRepository,
    OrderRepository,
    ProductRepository,
)
from app.routers import links, notes, orders, products
from app.settings import Settings, settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


def create_lifespan(
    configuration: Settings,
) -> Callable[[FastAPI], AbstractAsyncContextManager[None]]:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        print("[DB] Energy laboratory stores connected")
        application.state.settings = configuration
        application.state.products = ProductRepository()
        application.state.orders = OrderRepository()
        application.state.notes = NotesRepository()
        application.state.links = LinkRepository(configuration.short_code_length)
        application.state.users = deepcopy(USER_SEED)
        application.state.request_log = deque(maxlen=configuration.request_log_capacity)
        application.state.db_connected = True
        yield
        application.state.db_connected = False
        print("[DB] Energy laboratory stores disconnected")

    return lifespan


def create_app(configuration: Settings | None = None) -> FastAPI:
    active_settings = configuration or settings
    application = FastAPI(
        title="Energy Control Room API",
        description="Routing, Pydantic, dependency injection and middleware laboratory",
        version="1.0.0",
        lifespan=create_lifespan(active_settings),
        dependencies=[Depends(log_user_agent)],
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    application.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list(active_settings.allowed_hosts),
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(active_settings.cors_origins),
        allow_methods=list(active_settings.cors_methods),
        allow_headers=list(active_settings.cors_headers),
    )
    application.add_middleware(
        SimpleRateLimiter,
        limit=active_settings.rate_limit,
        window=active_settings.rate_window_seconds,
    )
    application.middleware("http")(create_tracing_middleware())
    application.add_exception_handler(LinkNotFoundError, link_not_found_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @application.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    application.include_router(products.router)
    application.include_router(orders.router)
    application.include_router(notes.router)
    application.include_router(notes.admin_router)
    application.include_router(links.admin_router)
    application.include_router(links.router)
    return application


app = create_app()


def run() -> None:
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=False)
