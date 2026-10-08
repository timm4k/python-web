import asyncio
from collections import defaultdict
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from time import monotonic, perf_counter
from typing import Any
from uuid import uuid4

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

UNLIMITED_PATH_PREFIXES = (
    "/static/",
    "/products",
    "/api/v1/orders",
    "/api/v1/notes",
    "/api/v1/admin",
    "/admin/requests-log",
)


class SimpleRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app: Any, limit: int, window: int) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.requests: defaultdict[str, list[float]] = defaultdict(list)
        self.lock = asyncio.Lock()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path == "/" or request.url.path.startswith(
            UNLIMITED_PATH_PREFIXES
        ):
            return await call_next(request)
        client_key = request.client.host if request.client else "unknown"
        now = monotonic()
        async with self.lock:
            timestamps = self.requests[client_key]
            threshold = now - self.window
            self.requests[client_key] = [
                timestamp for timestamp in timestamps if timestamp > threshold
            ]
            timestamps = self.requests[client_key]
            if len(timestamps) >= self.limit:
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "RATE_LIMITED",
                        "message": "Request limit exceeded",
                    },
                )
            timestamps.append(now)
        return await call_next(request)


def create_tracing_middleware() -> (
    Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]
):
    async def trace_request(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started = perf_counter()
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response = await call_next(request)
        process_time = f"{perf_counter() - started:.4f}s"
        response.headers["X-Process-Time"] = process_time
        response.headers["X-Request-ID"] = request_id
        request.app.state.request_log.append(
            {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "timestamp": datetime.now(UTC),
            }
        )
        return response

    return trace_request
