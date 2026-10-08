from dataclasses import dataclass
from os import getenv

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_PRODUCT_ADMIN_KEY = "energy-catalog-admin"
DEFAULT_LINK_ADMIN_KEY = "energy-link-admin-2026"
DEFAULT_RATE_LIMIT = 10
DEFAULT_RATE_WINDOW_SECONDS = 60
DEFAULT_REQUEST_LOG_CAPACITY = 100
DEFAULT_SHORT_CODE_LENGTH = 6
DEFAULT_ALLOWED_HOSTS = ("localhost", "127.0.0.1", "energy-frontend.example.com")
DEFAULT_CORS_ORIGINS = ("http://localhost:3000", "https://energy-frontend.example.com")
DEFAULT_CORS_METHODS = ("GET", "POST", "DELETE")
DEFAULT_CORS_HEADERS = ("Content-Type", "X-Admin-Key", "X-Request-ID")


def read_int(name: str, default: int) -> int:
    value = getenv(name)
    return int(value) if value is not None else default


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    product_admin_key: str = DEFAULT_PRODUCT_ADMIN_KEY
    link_admin_key: str = DEFAULT_LINK_ADMIN_KEY
    rate_limit: int = DEFAULT_RATE_LIMIT
    rate_window_seconds: int = DEFAULT_RATE_WINDOW_SECONDS
    request_log_capacity: int = DEFAULT_REQUEST_LOG_CAPACITY
    short_code_length: int = DEFAULT_SHORT_CODE_LENGTH
    allowed_hosts: tuple[str, ...] = DEFAULT_ALLOWED_HOSTS
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS
    cors_methods: tuple[str, ...] = DEFAULT_CORS_METHODS
    cors_headers: tuple[str, ...] = DEFAULT_CORS_HEADERS

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            host=getenv("APP_HOST", DEFAULT_HOST),
            port=read_int("APP_PORT", DEFAULT_PORT),
            product_admin_key=getenv("PRODUCT_ADMIN_KEY", DEFAULT_PRODUCT_ADMIN_KEY),
            link_admin_key=getenv("LINK_ADMIN_KEY", DEFAULT_LINK_ADMIN_KEY),
            rate_limit=read_int("RATE_LIMIT", DEFAULT_RATE_LIMIT),
            rate_window_seconds=read_int(
                "RATE_WINDOW_SECONDS", DEFAULT_RATE_WINDOW_SECONDS
            ),
            request_log_capacity=read_int(
                "REQUEST_LOG_CAPACITY", DEFAULT_REQUEST_LOG_CAPACITY
            ),
            short_code_length=read_int("SHORT_CODE_LENGTH", DEFAULT_SHORT_CODE_LENGTH),
        )


settings = Settings.from_environment()
