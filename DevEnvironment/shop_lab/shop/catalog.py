from typing import TypedDict


class Product(TypedDict):
    id: int
    name: str
    price: float


products: list[Product] = [
    {"id": 1, "name": "Ceramic Cat Bowl", "price": 420.00},
    {"id": 2, "name": "Feather Wand", "price": 185.50},
    {"id": 3, "name": "Window Hammock", "price": 960.00},
]


def get_product(product_id: int) -> Product | None:
    return next((product for product in products if product["id"] == product_id), None)
