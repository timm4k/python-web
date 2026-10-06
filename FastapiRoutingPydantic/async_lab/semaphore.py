import asyncio
from dataclasses import dataclass
from time import perf_counter

REQUEST_COUNT = 10
CONCURRENCY_LIMIT = 3

active_requests = 0
peak_active_requests = 0


@dataclass(frozen=True, slots=True)
class ConcurrencyRun:
    elapsed_seconds: float
    peak_active: int


@dataclass(frozen=True, slots=True)
class SemaphoreComparison:
    unlimited: ConcurrencyRun
    limited: ConcurrencyRun


async def _perform_request(user_id: int, delay: float) -> dict[str, int | str]:
    global active_requests, peak_active_requests

    active_requests += 1
    peak_active_requests = max(peak_active_requests, active_requests)
    print(f"[Sample {user_id:02d}] Entered analyzer · active {active_requests}")
    try:
        await asyncio.sleep(delay)
        return {"user_id": user_id, "status": "success"}
    finally:
        active_requests -= 1
        print(f"[Sample {user_id:02d}] Analysis finished · active {active_requests}")


async def api_request(
    user_id: int,
    semaphore: asyncio.Semaphore | None = None,
    delay: float = 1.0,
) -> dict[str, int | str]:
    if semaphore is None:
        return await _perform_request(user_id, delay)
    async with semaphore:
        return await _perform_request(user_id, delay)


async def run_requests(limit: int | None, delay: float = 1.0) -> ConcurrencyRun:
    global active_requests, peak_active_requests

    active_requests = 0
    peak_active_requests = 0
    semaphore = asyncio.Semaphore(limit) if limit is not None else None
    started = perf_counter()
    await asyncio.gather(
        *(api_request(user_id, semaphore, delay) for user_id in range(1, REQUEST_COUNT + 1))
    )
    return ConcurrencyRun(perf_counter() - started, peak_active_requests)


async def compare_concurrency_limits(delay: float = 1.0) -> SemaphoreComparison:
    print("\nUNLIMITED ANALYZER CHANNELS")
    unlimited = await run_requests(None, delay)
    print(f"Time: {unlimited.elapsed_seconds:.2f}s · Peak: {unlimited.peak_active}")
    print(f"\nANALYZER CAPACITY WITH SEMAPHORE({CONCURRENCY_LIMIT})")
    limited = await run_requests(CONCURRENCY_LIMIT, delay)
    print(f"Time: {limited.elapsed_seconds:.2f}s · Peak: {limited.peak_active}")
    return SemaphoreComparison(unlimited=unlimited, limited=limited)


if __name__ == "__main__":
    asyncio.run(compare_concurrency_limits())
