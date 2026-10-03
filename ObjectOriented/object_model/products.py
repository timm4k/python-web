import math


class Product:
    def __init__(self, name: str, price: float) -> None:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Product name is required")
        self.name = normalized_name
        self.price = price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, value: object) -> None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Price must be a number")
        if not math.isfinite(value) or value < 0:
            raise ValueError("Price must be a finite non-negative number")
        self._price = float(value)

    @price.deleter
    def price(self) -> None:
        raise AttributeError("Price cannot be deleted")


def main() -> None:
    perfume = Product("Violet Archive", 2800)
    print(f"Valid price: {perfume.price:.2f}")
    price_attribute = "price"
    for invalid_value in ("expensive", -10):
        try:
            setattr(perfume, price_attribute, invalid_value)
        except (TypeError, ValueError) as error:
            print(f"Rejected {invalid_value!r}: {error}")
    try:
        del perfume.price
    except AttributeError as error:
        print(f"Delete rejected: {error}")


if __name__ == "__main__":
    main()
