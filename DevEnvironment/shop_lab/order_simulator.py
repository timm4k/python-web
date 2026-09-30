import json
import random
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from shop_lab.shop.catalog import products

GENERATED_DIRECTORY = Path(__file__).resolve().parent / "generated"
ORDERS_FILE = GENERATED_DIRECTORY / "orders.json"
CUSTOMERS = ["Avery Stone", "Jordan Reed", "Morgan Hale", "Casey Quinn"]


class OrderRecord(TypedDict):
    id: int
    customer: str
    product: str
    price: float
    timestamp: str


def generate_random_order(order_id: int) -> OrderRecord:
    if order_id < 1:
        raise ValueError("Order ID must be positive")
    product = random.choice(products)
    return {
        "id": order_id,
        "customer": random.choice(CUSTOMERS),
        "product": product["name"],
        "price": product["price"],
        "timestamp": datetime.now().astimezone().isoformat(),
    }


def generate_orders(count: int = 5) -> list[OrderRecord]:
    if count < 1:
        raise ValueError("Order count must be positive")
    return [generate_random_order(order_id) for order_id in range(1, count + 1)]


def save_orders(orders: list[OrderRecord], output_path: Path = ORDERS_FILE) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(orders, indent=4), encoding="utf-8")
    return output_path


def main() -> None:
    orders = generate_orders()
    output_path = save_orders(orders)
    print(f"Generated {len(orders)} cat shop orders")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    main()
