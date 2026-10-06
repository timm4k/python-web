import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import perf_counter


@dataclass(frozen=True, slots=True)
class Assay:
    name: str
    duration: float


@dataclass(frozen=True, slots=True)
class AssayComparison:
    sequential_seconds: float
    concurrent_seconds: float
    assays: tuple[str, ...]


ASSAYS = (
    Assay("Vitamin D", 3.0),
    Assay("Ferritin", 5.0),
    Assay("Vitamin B12", 2.0),
)


async def run_assay(assay: Assay, time_scale: float = 1.0) -> str:
    print(f"[{assay.name}] Analysis started ({assay.duration:.0f}s)")
    await asyncio.sleep(assay.duration * time_scale)
    print(f"[{assay.name}] Result ready")
    return assay.name


async def cook_soup(time_scale: float = 1.0) -> str:
    return await run_assay(ASSAYS[0], time_scale)


async def cook_main_dish(time_scale: float = 1.0) -> str:
    return await run_assay(ASSAYS[1], time_scale)


async def bake_dessert(time_scale: float = 1.0) -> str:
    return await run_assay(ASSAYS[2], time_scale)


COOKING_STEPS: tuple[Callable[[float], Awaitable[str]], ...] = (
    cook_soup,
    cook_main_dish,
    bake_dessert,
)


async def sequential_cooking(time_scale: float = 1.0) -> tuple[list[str], float]:
    started = perf_counter()
    results = [await step(time_scale) for step in COOKING_STEPS]
    return results, perf_counter() - started


async def concurrent_cooking(time_scale: float = 1.0) -> tuple[list[str], float]:
    started = perf_counter()
    results = await asyncio.gather(*(step(time_scale) for step in COOKING_STEPS))
    return list(results), perf_counter() - started


async def compare_execution_modes(time_scale: float = 1.0) -> AssayComparison:
    print("\nSEQUENTIAL SAMPLE ANALYSIS")
    sequential_results, sequential_seconds = await sequential_cooking(time_scale)
    print(f"Total: {sequential_seconds:.2f}s")
    print("\nCONCURRENT SAMPLE ANALYSIS")
    concurrent_results, concurrent_seconds = await concurrent_cooking(time_scale)
    print(f"Total: {concurrent_seconds:.2f}s")
    if sequential_results != concurrent_results:
        raise RuntimeError("Analysis modes returned different assay results")
    return AssayComparison(
        sequential_seconds=sequential_seconds,
        concurrent_seconds=concurrent_seconds,
        assays=tuple(concurrent_results),
    )


if __name__ == "__main__":
    asyncio.run(compare_execution_modes())
