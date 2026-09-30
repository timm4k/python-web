from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Literal, TypedDict

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.concepts import (
    CatCategory,
    CatFact,
    ConceptExample,
    get_concept_examples,
    query_cat_facts,
)
from app.converter import convert_number
from app.environment import read_runtime_environment
from app.shop_lab_api import router as shop_lab_router

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
STATIC_DIRECTORY = BASE_DIRECTORY / "static"
PACKAGE_NAME = "purrfect-python-lab"

try:
    APPLICATION_VERSION = version(PACKAGE_NAME)
except PackageNotFoundError:
    APPLICATION_VERSION = "development"

app = FastAPI(title="Purrfect Python Lab", version=APPLICATION_VERSION)
app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")
app.include_router(shop_lab_router)


class EnvironmentSnapshot(TypedDict):
    pythonVersion: str
    operatingSystem: str
    architecture: str
    virtualEnvironment: bool


class ConversionRequest(BaseModel):
    value: str = Field(min_length=1, max_length=64)
    from_base: Literal[2, 10, 16]
    to_base: Literal[2, 10, 16]


class ConversionResponse(BaseModel):
    original: str
    result: str
    from_base: int
    to_base: int


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(STATIC_DIRECTORY / "index.html")


@app.get("/shop-lab", include_in_schema=False)
async def shop_lab() -> FileResponse:
    return FileResponse(STATIC_DIRECTORY / "shop-lab.html")


@app.get("/api/environment")
async def environment() -> EnvironmentSnapshot:
    runtime = read_runtime_environment()
    return {
        "pythonVersion": runtime.python_version,
        "operatingSystem": runtime.operating_system,
        "architecture": runtime.architecture,
        "virtualEnvironment": runtime.virtual_environment,
    }


@app.get("/api/cats")
async def cat_facts(
    category: CatCategory | None = None,
    keyword: str | None = Query(default=None, min_length=1, max_length=40),
    sort_by_title: bool = False,
) -> list[CatFact]:
    return query_cat_facts(category, keyword, sort_by_title)


@app.get("/api/concepts")
async def concepts() -> list[ConceptExample]:
    return get_concept_examples()


@app.post("/api/convert")
async def convert(request: ConversionRequest) -> ConversionResponse:
    try:
        result = convert_number(request.value, request.from_base, request.to_base)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return ConversionResponse(
        original=request.value,
        result=result,
        from_base=request.from_base,
        to_base=request.to_base,
    )
