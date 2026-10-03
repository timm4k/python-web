import math
from typing import Self, overload


class NonNegativeNumber:
    def __set_name__(self, owner: type[object], name: str) -> None:
        self.name = name
        self.private_name = f"_{name}"

    @overload
    def __get__(self, instance: None, owner: type[object]) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type[object]) -> float: ...

    def __get__(self, instance: object | None, owner: type[object]) -> Self | float:
        if instance is None:
            return self
        value = getattr(instance, self.private_name)
        if not isinstance(value, float):
            raise TypeError(f"Stored {self.name} must be a float")
        return value

    def __set__(self, instance: object, value: float) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{self.name} must be a finite non-negative number")
        setattr(instance, self.private_name, float(value))


class Car:
    mileage = NonNegativeNumber()
    fuel_capacity = NonNegativeNumber()

    def __init__(self, brand: str, mileage: float, fuel_capacity: float) -> None:
        self.brand = brand
        self.mileage = mileage
        self.fuel_capacity = fuel_capacity


def main() -> None:
    car = Car("Toyota", 15_000, 50)
    print(f"{car.brand}: {car.mileage:.0f} km · {car.fuel_capacity:.1f} L")
    invalid_values: tuple[tuple[str, object], ...] = (
        ("mileage", -100),
        ("fuel_capacity", "full tank"),
    )
    for field_name, value in invalid_values:
        try:
            setattr(car, field_name, value)
        except (TypeError, ValueError) as error:
            print(f"Rejected {field_name}: {error}")


if __name__ == "__main__":
    main()
