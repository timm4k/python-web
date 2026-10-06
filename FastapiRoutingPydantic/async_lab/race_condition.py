import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

INITIAL_BALANCE = 1_000
WITHDRAWAL_AMOUNT = 300
CLIENT_COUNT = 5

bank_balance = INITIAL_BALANCE
lock = asyncio.Lock()


@dataclass(frozen=True, slots=True)
class WithdrawalComparison:
    unsafe_balance: int
    safe_balance: int
    safe_approved: int


async def _withdraw(amount: int, client_id: int, delay: float, locked: bool) -> bool:
    global bank_balance

    if bank_balance < amount:
        print(f"[Analyzer {client_id}] Rejected: insufficient reagent")
        return False
    state = "Lock acquired" if locked else f"Observed {bank_balance} µL"
    print(f"[Analyzer {client_id}] {state}, reserving {amount} µL")
    await asyncio.sleep(delay)
    bank_balance -= amount
    print(f"[Analyzer {client_id}] Reservation completed, remaining {bank_balance} µL")
    return True


async def withdraw(amount: int, client_id: int, delay: float = 0.01) -> bool:
    return await _withdraw(amount, client_id, delay, False)


async def withdraw_safe(amount: int, client_id: int, delay: float = 0.01) -> bool:
    async with lock:
        return await _withdraw(amount, client_id, delay, True)


async def _run_withdrawals(
    operation: Callable[[int, int, float], Awaitable[bool]],
    delay: float,
) -> list[bool]:
    return list(
        await asyncio.gather(
            *(
                operation(WITHDRAWAL_AMOUNT, client_id, delay)
                for client_id in range(1, CLIENT_COUNT + 1)
            )
        )
    )


async def compare_withdrawals(delay: float = 0.01) -> WithdrawalComparison:
    global bank_balance

    print("\nUNSYNCHRONIZED REAGENT ACCESS")
    bank_balance = INITIAL_BALANCE
    await _run_withdrawals(withdraw, delay)
    unsafe_balance = bank_balance
    print(f"Final reagent volume: {unsafe_balance} µL")

    print("\nSYNCHRONIZED REAGENT ACCESS WITH ASYNCIO.LOCK")
    bank_balance = INITIAL_BALANCE
    approvals = await _run_withdrawals(withdraw_safe, delay)
    safe_balance = bank_balance
    print(f"Final reagent volume: {safe_balance} µL")

    return WithdrawalComparison(
        unsafe_balance=unsafe_balance,
        safe_balance=safe_balance,
        safe_approved=sum(approvals),
    )


if __name__ == "__main__":
    asyncio.run(compare_withdrawals())
