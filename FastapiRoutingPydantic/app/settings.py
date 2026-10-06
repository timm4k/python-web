import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = os.getenv("APP_HOST", "127.0.0.1")
    port: int = int(os.getenv("APP_PORT", "8000"))
    api_prefix: str = "/api/v1"
    admin_key: str = os.getenv("APP_ADMIN_KEY", "admin-secret-123")
    fibonacci_input: int = int(os.getenv("BENCHMARK_FIBONACCI_INPUT", "35"))
    io_delay_seconds: float = float(os.getenv("BENCHMARK_IO_DELAY", "1"))
    default_borrow_days: int = 14
    max_borrow_days: int = 60
    max_active_bookings: int = 3
    benchmark_request_count: int = 10

    @property
    def benchmark_base_url(self) -> str:
        return f"http://{self.host}:{self.port}{self.api_prefix}/benchmark"


settings = Settings()
