from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .schemas import CollectionRequest, FactoryRequest, RetryRequest, SessionRequest
from .service import (
    movie_protocols,
    overview,
    run_collection,
    run_factory,
    run_retry,
    run_session,
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Python Protocol Explorer", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/overview")
def get_overview() -> dict[str, object]:
    return overview()


@app.get("/api/movie-protocols")
def get_movie_protocols() -> dict[str, object]:
    return movie_protocols()


@app.post("/api/collection")
def collection(request: CollectionRequest) -> dict[str, object]:
    try:
        return run_collection(request)
    except IndexError as error:
        raise HTTPException(status_code=400, detail="Collection index is out of range") from error


@app.post("/api/factory")
def factory(request: FactoryRequest) -> dict[str, object]:
    try:
        return run_factory(request)
    except (TypeError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/retry")
def retry_demo(request: RetryRequest) -> dict[str, object]:
    return run_retry(request)


@app.post("/api/session")
def session_demo(request: SessionRequest) -> dict[str, object]:
    try:
        return run_session(request)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
