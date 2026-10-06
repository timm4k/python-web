from enum import StrEnum
from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

from async_lab.event_loop import compare_execution_modes
from async_lab.race_condition import compare_withdrawals
from async_lab.semaphore import compare_concurrency_limits
from async_lab.task_grouping import gather_collect, gather_fail_fast, task_group

from ..service_config import ServiceConfig

router = APIRouter(prefix="/experiments", tags=["Interactive experiments"])


class EventLoopRead(BaseModel):
    sequential_seconds: float
    concurrent_seconds: float
    speedup: float
    explanation: str


class RaceConditionRead(BaseModel):
    unsafe_balance: int
    safe_balance: int
    approved_with_lock: int
    explanation: str


class SemaphoreRead(BaseModel):
    unlimited_seconds: float
    limited_seconds: float
    unlimited_peak: int
    limited_peak: int
    explanation: str


class ConfigRead(BaseModel):
    service_name: str
    environment: str
    debug_mode: bool
    database_host: str
    masked_secret: str


class GroupingStrategy(StrEnum):
    GATHER_FAIL_FAST = "gather-fail-fast"
    GATHER_COLLECT = "gather-collect"
    TASK_GROUP = "task-group"


class GroupingRead(BaseModel):
    strategy: GroupingStrategy
    completed: int
    errors: int
    cancelled: int
    behavior: str


@router.get("/event-loop", response_model=EventLoopRead)
async def event_loop_experiment(
    time_scale: Annotated[float, Query(gt=0, le=0.2)] = 0.04,
) -> EventLoopRead:
    result = await compare_execution_modes(time_scale)
    return EventLoopRead(
        sequential_seconds=round(result.sequential_seconds, 3),
        concurrent_seconds=round(result.concurrent_seconds, 3),
        speedup=round(result.sequential_seconds / result.concurrent_seconds, 2),
        explanation="Sequential waits add together; concurrent waits overlap at await points",
    )


@router.get("/race-condition", response_model=RaceConditionRead)
async def race_condition_experiment() -> RaceConditionRead:
    result = await compare_withdrawals(delay=0.005)
    return RaceConditionRead(
        unsafe_balance=result.unsafe_balance,
        safe_balance=result.safe_balance,
        approved_with_lock=result.safe_approved,
        explanation="Lock keeps the balance check and update inside one protected section",
    )


@router.get("/task-grouping", response_model=GroupingRead)
async def task_grouping_experiment(
    strategy: GroupingStrategy = GroupingStrategy.GATHER_FAIL_FAST,
) -> GroupingRead:
    if strategy is GroupingStrategy.GATHER_COLLECT:
        result = await gather_collect(delay=0.08)
        behavior = "All tasks finish and exceptions occupy positions in the result list"
    elif strategy is GroupingStrategy.TASK_GROUP:
        result = await task_group(delay=0.08)
        behavior = "A failure cancels unfinished siblings and leaves the group as one unit"
    else:
        result = await gather_fail_fast(delay=0.08)
        behavior = "The first exception reaches the caller while sibling tasks keep running"
    return GroupingRead(
        strategy=strategy,
        completed=len(result.completed),
        errors=len(result.errors),
        cancelled=result.cancelled,
        behavior=behavior,
    )


@router.get("/semaphore", response_model=SemaphoreRead)
async def semaphore_experiment() -> SemaphoreRead:
    result = await compare_concurrency_limits(delay=0.04)
    return SemaphoreRead(
        unlimited_seconds=round(result.unlimited.elapsed_seconds, 3),
        limited_seconds=round(result.limited.elapsed_seconds, 3),
        unlimited_peak=result.unlimited.peak_active,
        limited_peak=result.limited.peak_active,
        explanation="Semaphore allows at most three requests into the protected operation",
    )


@router.post("/validate-config", response_model=ConfigRead)
async def validate_config(payload: ServiceConfig) -> ConfigRead:
    return ConfigRead(
        service_name=payload.service_name,
        environment=payload.environment,
        debug_mode=payload.debug_mode,
        database_host=str(payload.database.host),
        masked_secret=str(payload.secret_key),
    )
