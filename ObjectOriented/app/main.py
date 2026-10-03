from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.catalog_api import router as catalog_router
from app.contracts_api import router as contracts_router
from app.object_api import router as object_router

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
STATIC_DIRECTORY = BASE_DIRECTORY / "static"
PACKAGE_NAME = "perfume-object-lab"

try:
    APPLICATION_VERSION = version(PACKAGE_NAME)
except PackageNotFoundError:
    APPLICATION_VERSION = "development"

app = FastAPI(title="Perfume Object Laboratory", version=APPLICATION_VERSION)
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")
app.include_router(catalog_router)
app.include_router(object_router)
app.include_router(contracts_router)


@app.get("/", include_in_schema=False)
def object_model_page() -> FileResponse:
    return FileResponse(STATIC_DIRECTORY / "object-model.html")


@app.get("/contracts", include_in_schema=False)
def contracts_page() -> FileResponse:
    return FileResponse(STATIC_DIRECTORY / "contracts.html")
