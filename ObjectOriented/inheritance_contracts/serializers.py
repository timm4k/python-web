import json
from abc import ABC, abstractmethod
from typing import Protocol


class SerializerProtocol(Protocol):
    def dumps(self, data: object) -> bytes: ...

    def loads(self, raw: bytes) -> object: ...


class JsonSerializer:
    def dumps(self, data: object) -> bytes:
        return json.dumps(data).encode("utf-8")

    def loads(self, raw: bytes) -> object:
        result: object = json.loads(raw.decode("utf-8"))
        return result


class SimpleSerializer:
    def dumps(self, data: object) -> bytes:
        return str(data).encode("utf-8")

    def loads(self, raw: bytes) -> object:
        return raw.decode("utf-8")


class BaseStorage(ABC):
    def __init__(self, serializer: SerializerProtocol) -> None:
        self._serializer = serializer

    @abstractmethod
    def save(self, key: str, data: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, key: str) -> object | None:
        raise NotImplementedError


class InMemoryStorage(BaseStorage):
    def __init__(self, serializer: SerializerProtocol) -> None:
        super().__init__(serializer)
        self._records: dict[str, bytes] = {}

    def save(self, key: str, data: object) -> None:
        if not key.strip():
            raise ValueError("Storage key is required")
        self._records[key] = self._serializer.dumps(data)

    def load(self, key: str) -> object | None:
        raw = self._records.get(key)
        return None if raw is None else self._serializer.loads(raw)


def main() -> None:
    json_storage = InMemoryStorage(JsonSerializer())
    json_storage.save("scent", {"name": "Violet Archive", "notes": ["iris", "musk"]})
    print(f"JSON storage: {json_storage.load('scent')}")
    simple_storage = InMemoryStorage(SimpleSerializer())
    simple_storage.save("scent", "Violet Archive")
    print(f"Simple storage: {simple_storage.load('scent')}")


if __name__ == "__main__":
    main()
