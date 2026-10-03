from abc import ABC, abstractmethod
from typing import Self


class DataStore(ABC):
    @property
    @abstractmethod
    def connection_string(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_config(cls, config: dict[str, object]) -> Self:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def validate_config(config: dict[str, object]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def execute(self, query: str) -> list[object]:
        raise NotImplementedError


class PostgreSQLStore(DataStore):
    DEFAULT_PORT = 5432

    def __init__(self, host: str, port: int, database: str) -> None:
        if not host or not database:
            raise ValueError("Host and database are required")
        if port not in range(1, 65536):
            raise ValueError("Port must be between 1 and 65535")
        self._connection_string = f"postgresql://{host}:{port}/{database}"

    @property
    def connection_string(self) -> str:
        return self._connection_string

    @classmethod
    def from_config(cls, config: dict[str, object]) -> Self:
        if not cls.validate_config(config):
            raise ValueError("Config requires string host and database values")
        host = config["host"]
        database = config["db"]
        port = config.get("port", cls.DEFAULT_PORT)
        if not isinstance(host, str) or not isinstance(database, str) or not isinstance(port, int):
            raise TypeError("Host and database must be strings and port must be an integer")
        return cls(host, port, database)

    @staticmethod
    def validate_config(config: dict[str, object]) -> bool:
        return isinstance(config.get("host"), str) and isinstance(config.get("db"), str)

    def execute(self, query: str) -> list[object]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Query is required")
        print(f"[PG] Executing: {normalized_query}")
        return []


def main() -> None:
    config: dict[str, object] = {"host": "localhost", "db": "perfume_lab"}
    print(f"Valid config: {PostgreSQLStore.validate_config(config)}")
    store = PostgreSQLStore.from_config(config)
    print(f"Connection: {store.connection_string}")
    print(f"Query result: {store.execute('SELECT 1')}")


if __name__ == "__main__":
    main()
