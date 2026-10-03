from collections.abc import Sequence

from inheritance_contracts.vehicles import Car, ElectricCar, Vehicle


def all_subclasses(base_class: type[object]) -> set[type[object]]:
    direct = set(base_class.__subclasses__())
    return direct | {descendant for child in direct for descendant in all_subclasses(child)}


def class_names(classes: Sequence[type[object]]) -> list[str]:
    return [item.__name__ for item in classes]


def main() -> None:
    tesla = ElectricCar("Tesla", 2024, 75)
    direct_base = ElectricCar.__base__
    print(f"Direct base: {direct_base.__name__ if direct_base is not None else 'None'}")
    print(f"Bases: {class_names(list(ElectricCar.__bases__))}")
    print(f"MRO: {class_names(list(ElectricCar.__mro__))}")
    print(f"Vehicle direct subclasses: {class_names(Vehicle.__subclasses__())}")
    print(f"Car direct subclasses: {class_names(Car.__subclasses__())}")
    print(f"All Vehicle descendants: {sorted(cls.__name__ for cls in all_subclasses(Vehicle))}")
    for target in (ElectricCar, Car, Vehicle, object):
        print(f"isinstance(tesla, {target.__name__}): {isinstance(tesla, target)}")
    print(f"issubclass(ElectricCar, Vehicle): {issubclass(ElectricCar, Vehicle)}")
    print(f"issubclass(Vehicle, ElectricCar): {issubclass(Vehicle, ElectricCar)}")


if __name__ == "__main__":
    main()
