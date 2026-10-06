import time
from collections.abc import Callable
from functools import wraps

Reporter = Callable[[str], None]


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started_at
            print(f"[timed] {func.__name__} → {elapsed:.4f}s")

    return wrapper


def retry[**P, R](
    max_attempts: int = 3,
    delay: float = 1.0,
    reporter: Reporter = print,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int):
        raise TypeError("max_attempts must be an integer")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least one")
    if isinstance(delay, bool) or not isinstance(delay, (int, float)):
        raise TypeError("delay must be a number")
    if delay < 0:
        raise ValueError("delay cannot be negative")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_error: Exception | None = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    last_error = error
                    reporter(f"[retry] Attempt {attempt}/{max_attempts} failed: {error}")
                    if attempt < max_attempts and delay:
                        time.sleep(delay)
            raise RuntimeError(
                f"{func.__name__} failed after {max_attempts} attempts"
            ) from last_error

        return wrapper

    return decorator


def create_unstable_api_call(
    failures_before_success: int = 2,
    max_attempts: int | None = None,
    delay: float = 0.1,
    reporter: Reporter = print,
) -> Callable[[str], str]:
    if isinstance(failures_before_success, bool) or not isinstance(failures_before_success, int):
        raise TypeError("failures_before_success must be an integer")
    if failures_before_success < 0:
        raise ValueError("failures_before_success cannot be negative")
    attempt_limit = failures_before_success + 1 if max_attempts is None else max_attempts
    attempts = 0

    @timed
    @retry(max_attempts=attempt_limit, delay=delay, reporter=reporter)
    def unstable_api_call(url: str) -> str:
        """Simulate an unstable API request"""
        nonlocal attempts
        attempts += 1
        if attempts <= failures_before_success:
            raise ConnectionError("Connection lost")
        return f"200 OK: {url}"

    return unstable_api_call


def main() -> None:
    unstable_api_call = create_unstable_api_call()
    print(unstable_api_call("https://api.example.com/data"))
    print(f"Function name: {unstable_api_call.__name__}")
    print(f"Documentation: {unstable_api_call.__doc__}")


if __name__ == "__main__":
    main()
