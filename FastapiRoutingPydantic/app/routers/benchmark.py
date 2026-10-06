import asyncio
import time
from time import perf_counter

from fastapi import APIRouter
from pydantic import BaseModel

from ..settings import settings

router = APIRouter(prefix="/benchmark", tags=["Async and sync benchmark"])


class BenchmarkRead(BaseModel):
    mode: str
    duration_seconds: float
    result: int | None = None


def fibonacci(number: int) -> int:
    if number <= 1:
        return number
    return fibonacci(number - 1) + fibonacci(number - 2)


@router.get("/cpu-bound-sync", response_model=BenchmarkRead)
def cpu_bound_sync() -> BenchmarkRead:
    started = perf_counter()
    result = fibonacci(settings.fibonacci_input)
    return BenchmarkRead(
        mode="cpu-bound-sync",
        result=result,
        duration_seconds=round(perf_counter() - started, 4),
    )


@router.get("/cpu-bound-async", response_model=BenchmarkRead)
async def cpu_bound_async() -> BenchmarkRead:
    started = perf_counter()
    result = fibonacci(settings.fibonacci_input)
    return BenchmarkRead(
        mode="cpu-bound-async",
        result=result,
        duration_seconds=round(perf_counter() - started, 4),
    )


@router.get("/io-bound-sync", response_model=BenchmarkRead)
def io_bound_sync() -> BenchmarkRead:
    started = perf_counter()
    time.sleep(settings.io_delay_seconds)
    return BenchmarkRead(
        mode="io-bound-sync",
        duration_seconds=round(perf_counter() - started, 4),
    )


@router.get("/io-bound-async", response_model=BenchmarkRead)
async def io_bound_async() -> BenchmarkRead:
    started = perf_counter()
    await asyncio.sleep(settings.io_delay_seconds)
    return BenchmarkRead(
        mode="io-bound-async",
        duration_seconds=round(perf_counter() - started, 4),
    )
