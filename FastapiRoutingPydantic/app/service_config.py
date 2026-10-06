from enum import StrEnum
from typing import Annotated, Self

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    IPvAnyAddress,
    SecretStr,
    model_validator,
)
from pydantic_core import Url

DATABASE_NAME_PATTERN = r"^[A-Za-z0-9_]+$"


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


def validate_redis_url(value: Url) -> Url:
    if value.scheme not in {"redis", "rediss"}:
        raise ValueError("URL scheme must be redis or rediss")
    return value


type RedisUrl = Annotated[Url, AfterValidator(validate_redis_url)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Credentials(StrictModel):
    username: str = Field(min_length=3)
    password: SecretStr = Field(min_length=8)


class DatabaseConfig(StrictModel):
    host: IPvAnyAddress
    port: int = Field(ge=1024, le=65535)
    database_name: str = Field(min_length=3, pattern=DATABASE_NAME_PATTERN)
    credentials: Credentials


class RedisConfig(StrictModel):
    connection_url: RedisUrl
    ttl_seconds: int = Field(ge=60, le=86_400)


class ServiceConfig(StrictModel):
    service_name: str = Field(min_length=3, max_length=50)
    environment: Environment
    debug_mode: bool = False
    database: DatabaseConfig
    redis: RedisConfig
    admin_emails: list[EmailStr] = Field(min_length=1, max_length=5)
    secret_key: SecretStr = Field(min_length=32)

    @model_validator(mode="after")
    def disable_production_debug(self) -> Self:
        if self.environment is Environment.PRODUCTION:
            self.debug_mode = False
        return self


VALID_CONFIG: dict[str, object] = {
    "service_name": "vitamin-analysis-service",
    "environment": "production",
    "debug_mode": False,
    "database": {
        "host": "192.168.1.100",
        "port": 5432,
        "database_name": "vitamin_results",
        "credentials": {"username": "lab_admin", "password": "strong-password"},
    },
    "redis": {"connection_url": "redis://localhost:6379", "ttl_seconds": 3600},
    "admin_emails": ["quality@vitalab.example", "support@vitalab.example"],
    "secret_key": "local-demonstration-secret-key-123456789",
}


def demonstrate_validation() -> None:
    print("VALID CONFIGURATION")
    config = ServiceConfig.model_validate(VALID_CONFIG)
    print(config)
    print(f"Secret is masked: {config.secret_key}")
    print("\nPRODUCTION DEBUG NORMALIZATION")
    production_debug = {**VALID_CONFIG, "debug_mode": True}
    normalized = ServiceConfig.model_validate(production_debug)
    print(f"Requested True · parsed value {normalized.debug_mode}")
    print("\nINVALID CONFIGURATION")
    invalid_config = {
        **VALID_CONFIG,
        "admin_emails": ["not-an-email"],
        "secret_key": "short",
    }
    try:
        ServiceConfig.model_validate(invalid_config)
    except ValueError as error:
        print(error)


if __name__ == "__main__":
    demonstrate_validation()
