import asyncio

from async_lab.event_loop import compare_execution_modes
from async_lab.race_condition import compare_withdrawals
from async_lab.semaphore import compare_concurrency_limits
from async_lab.task_grouping import (
    gather_collect,
    gather_fail_fast,
    task_group,
)


def test_concurrent_assays_are_faster() -> None:
    result = asyncio.run(compare_execution_modes(time_scale=0.001))

    assert result.assays == ("Vitamin D", "Ferritin", "Vitamin B12")
    assert result.concurrent_seconds < result.sequential_seconds


def test_grouping_strategies_expose_different_failure_semantics() -> None:
    fail_fast = asyncio.run(gather_fail_fast(delay=0.002))
    collected = asyncio.run(gather_collect(delay=0.002))
    grouped = asyncio.run(task_group(delay=0.2))

    assert len(fail_fast.completed) == 4
    assert len(fail_fast.errors) == 1
    assert len(collected.completed) == 4
    assert len(collected.errors) == 1
    assert grouped.errors == ("Sample 3 result download failed",)
    assert len(grouped.completed) + grouped.cancelled == 4
    assert grouped.cancelled > 0


def test_lock_preserves_balance_invariant() -> None:
    result = asyncio.run(compare_withdrawals(delay=0.001))

    assert result.unsafe_balance == -500
    assert result.safe_balance == 100
    assert result.safe_approved == 3


def test_semaphore_caps_peak_concurrency() -> None:
    result = asyncio.run(compare_concurrency_limits(delay=0.001))

    assert result.unlimited.peak_active == 10
    assert result.limited.peak_active == 3
