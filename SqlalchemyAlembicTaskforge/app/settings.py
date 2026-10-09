from dataclasses import dataclass
from os import getenv

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000


def read_port() -> int:
    value = int(getenv("APP_PORT", DEFAULT_PORT))
    if not 1 <= value <= 65_535:
        raise ValueError("APP_PORT must be between 1 and 65535")
    return value


def require_database_url() -> str:
    value = getenv("DATABASE_URL")
    if not value:
        raise RuntimeError("DATABASE_URL must be set before the application starts")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    host: str
    port: int

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(host=getenv("APP_HOST", DEFAULT_HOST), port=read_port())
