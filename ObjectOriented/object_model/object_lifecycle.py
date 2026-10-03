from typing import Self


class TracedObject:
    def __new__(cls, name: str) -> Self:
        print(f"1. __new__ called for {cls.__name__}")
        instance = super().__new__(cls)
        print(f"   Allocated object id: {id(instance)}")
        return instance

    def __init__(self, name: str) -> None:
        print(f"2. __init__ called for object id: {id(self)}")
        self.name = name


def create_invalid_initializer() -> type[object]:
    def invalid_init(instance: object) -> str:
        return "invalid return value"

    return type("InvalidInitializer", (), {"__init__": invalid_init})


def main() -> None:
    traced = TracedObject("Test")
    print(f"Initialized name: {traced.name}")
    try:
        create_invalid_initializer()()
    except TypeError as error:
        print(f"Invalid __init__ return: {error}")


if __name__ == "__main__":
    main()
