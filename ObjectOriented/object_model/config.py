from typing import ClassVar, Self


class AppSettings:
    _instance: ClassVar[Self | None] = None

    def __new__(cls, database_url: str, debug: bool = False) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, database_url: str, debug: bool = False) -> None:
        if hasattr(self, "_initialized"):
            return
        self.database_url = database_url
        self.debug = debug
        self._initialized = True


def main() -> None:
    first = AppSettings("postgresql://localhost/perfume", debug=True)
    second = AppSettings("mysql://production/perfume", debug=False)
    print(f"Same object: {first is second}")
    print(f"Preserved URL: {second.database_url}")
    print(f"Preserved debug mode: {second.debug}")


if __name__ == "__main__":
    main()
