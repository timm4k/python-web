class Vehicle:
    def __init__(self, brand: str, year: int) -> None:
        if not brand.strip():
            raise ValueError("Brand is required")
        if year < 1886:
            raise ValueError("Year must be 1886 or later")
        self.brand = brand.strip()
        self.year = year

    def start_engine(self) -> str:
        return f"{self.brand} ({self.year}) engine started"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(brand={self.brand!r}, year={self.year})"


class Car(Vehicle):
    def __init__(self, brand: str, year: int, num_doors: int = 4) -> None:
        super().__init__(brand, year)
        if num_doors < 1:
            raise ValueError("Door count must be positive")
        self.num_doors = num_doors

    def start_engine(self) -> str:
        return f"{super().start_engine()} [Safety belts checked]"


class ElectricCar(Car):
    def __init__(self, brand: str, year: int, battery_kwh: float, num_doors: int = 4) -> None:
        super().__init__(brand, year, num_doors)
        if battery_kwh <= 0:
            raise ValueError("Battery capacity must be positive")
        self.battery_kwh = float(battery_kwh)

    def start_engine(self) -> str:
        return f"{self.brand}: silent start · charge 100%"

    def charge(self, kwh: float) -> None:
        if kwh <= 0:
            raise ValueError("Charge amount must be positive")
        print(f"Charging {self.brand} with {kwh:g} kWh")


def create_sample_vehicles() -> tuple[Vehicle, Car, ElectricCar]:
    return (
        Vehicle("Atlas", 2020),
        Car("Volvo", 2022),
        ElectricCar("Tesla", 2024, 75),
    )


def main() -> None:
    vehicles = create_sample_vehicles()
    for vehicle in vehicles:
        print(f"{vehicle!r}: {vehicle.start_engine()}")
    vehicles[-1].charge(20)


if __name__ == "__main__":
    main()
