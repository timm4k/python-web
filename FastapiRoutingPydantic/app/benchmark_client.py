import asyncio
from dataclasses import dataclass
from time import perf_counter

import httpx

from .settings import settings

ENDPOINTS = (
    "cpu-bound-sync",
    "cpu-bound-async",
    "io-bound-sync",
    "io-bound-async",
)


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    endpoint: str
    request_count: int
    elapsed_seconds: float
    successful: int


async def send_requests(
    endpoint: str,
    count: int = settings.benchmark_request_count,
    base_url: str = settings.benchmark_base_url,
) -> BenchmarkResult:
    started = perf_counter()
    async with httpx.AsyncClient(timeout=180.0) as client:
        responses = await asyncio.gather(
            *(client.get(f"{base_url}/{endpoint}") for _ in range(count))
        )
    return BenchmarkResult(
        endpoint=endpoint,
        request_count=count,
        elapsed_seconds=perf_counter() - started,
        successful=sum(response.is_success for response in responses),
    )


async def main() -> None:
    print(f"{'Endpoint':<24} {'Requests':>8} {'Success':>8} {'Total':>10}")
    print("-" * 54)
    for endpoint in ENDPOINTS:
        result = await send_requests(endpoint, settings.benchmark_request_count)
        print(
            f"{result.endpoint:<24} {result.request_count:>8} "
            f"{result.successful:>8} {result.elapsed_seconds:>9.2f}s"
        )


if __name__ == "__main__":
    asyncio.run(main())
