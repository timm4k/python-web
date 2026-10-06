import asyncio
import random
from collections.abc import Coroutine
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class GroupingMode(StrEnum):
    GATHER_FAIL_FAST = "gather(return_exceptions=False)"
    GATHER_COLLECT = "gather(return_exceptions=True)"
    TASK_GROUP = "TaskGroup"


@dataclass(frozen=True, slots=True)
class GroupingResult:
    mode: GroupingMode
    completed: tuple[str, ...]
    errors: tuple[str, ...]
    cancelled: int


async def download_file(
    file_id: int,
    fail: bool = False,
    *,
    delay: float | None = None,
) -> str:
    actual_delay = delay if delay is not None else random.uniform(0.5, 2.0)
    print(f"[Sample {file_id}] Result download started ({actual_delay:.2f}s)")
    try:
        await asyncio.sleep(actual_delay / 2 if fail else actual_delay)
        if fail:
            raise ValueError(f"Sample {file_id} result download failed")
        result = f"file_{file_id}.dat"
        print(f"[Sample {file_id}] Result downloaded")
        return result
    except asyncio.CancelledError:
        print(f"[Sample {file_id}] Download cancelled")
        raise


def _download_coroutines(delay: float | None = None) -> list[Coroutine[Any, Any, str]]:
    return [download_file(file_id, file_id == 3, delay=delay) for file_id in range(1, 6)]


async def gather_fail_fast(delay: float | None = None) -> GroupingResult:
    tasks: list[asyncio.Task[str]] = [
        asyncio.create_task(coroutine) for coroutine in _download_coroutines(delay)
    ]
    errors: list[str] = []
    try:
        await asyncio.gather(*tasks, return_exceptions=False)
    except ValueError as error:
        errors.append(str(error))
        await asyncio.gather(*tasks, return_exceptions=True)
    completed = tuple(task.result() for task in tasks if task.done() and not task.exception())
    return GroupingResult(GroupingMode.GATHER_FAIL_FAST, completed, tuple(errors), 0)


async def gather_collect(delay: float | None = None) -> GroupingResult:
    raw_results = await asyncio.gather(*_download_coroutines(delay), return_exceptions=True)
    completed = tuple(result for result in raw_results if isinstance(result, str))
    errors = tuple(str(result) for result in raw_results if isinstance(result, Exception))
    return GroupingResult(GroupingMode.GATHER_COLLECT, completed, errors, 0)


async def task_group(delay: float | None = None) -> GroupingResult:
    tasks: list[asyncio.Task[str]] = []
    errors: list[str] = []
    try:
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(coroutine) for coroutine in _download_coroutines(delay)]
    except* ValueError as error_group:
        errors.extend(str(error) for error in error_group.exceptions)
    completed = tuple(
        task.result() for task in tasks if not task.cancelled() and task.exception() is None
    )
    cancelled = sum(task.cancelled() for task in tasks)
    return GroupingResult(GroupingMode.TASK_GROUP, completed, tuple(errors), cancelled)


async def compare_grouping_strategies(delay: float | None = None) -> tuple[GroupingResult, ...]:
    results = []
    for strategy in (gather_fail_fast, gather_collect, task_group):
        print(f"\n{strategy.__name__.replace('_', ' ').upper()}")
        result = await strategy(delay)
        print(
            f"Completed: {len(result.completed)} · Errors: {len(result.errors)}"
            f" · Cancelled: {result.cancelled}"
        )
        results.append(result)
    return tuple(results)


if __name__ == "__main__":
    asyncio.run(compare_grouping_strategies())
