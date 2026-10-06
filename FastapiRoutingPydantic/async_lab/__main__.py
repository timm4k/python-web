import asyncio

from .event_loop import compare_execution_modes
from .race_condition import compare_withdrawals
from .semaphore import compare_concurrency_limits
from .task_grouping import compare_grouping_strategies


def heading(title: str) -> None:
    print(f"\n{'=' * 68}\n{title}\n{'=' * 68}")


async def main() -> None:
    heading("BLOOD ASSAY SCHEDULING WITH THE EVENT LOOP")
    comparison = await compare_execution_modes()
    print(
        f"Sequential waits add up; concurrent time follows the longest assay: "
        f"{comparison.sequential_seconds:.2f}s vs {comparison.concurrent_seconds:.2f}s"
    )
    heading("LAB RESULT GROUPING AND FAILURE SEMANTICS")
    await compare_grouping_strategies()
    heading("SHARED REAGENT SAFETY WITH ASYNCIO.LOCK")
    await compare_withdrawals()
    heading("ANALYZER CAPACITY WITH ASYNCIO.SEMAPHORE")
    await compare_concurrency_limits()
    heading("ASYNC BLOOD ANALYSIS SHOWCASE COMPLETE")


if __name__ == "__main__":
    asyncio.run(main())
