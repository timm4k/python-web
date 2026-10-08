from __future__ import annotations

from collections.abc import Iterable
from copy import deepcopy
from datetime import UTC, datetime
from secrets import choice
from string import ascii_letters, digits
from typing import Any, cast

from app.models import (
    LinkCreate,
    NoteCreate,
    OrderCreate,
    OrderRead,
    OrderStatus,
    ProductCreate,
)

PRODUCT_SEED = [
    {
        "id": 1,
        "name": "Original Green",
        "category": "classic",
        "price": 89.0,
        "stock": 24,
        "flavor_profile": "Bold sweet energy profile with a crisp finish",
        "sugar_free": False,
    },
    {
        "id": 2,
        "name": "Ultra White",
        "category": "ultra",
        "price": 85.0,
        "stock": 40,
        "flavor_profile": "Light citrus profile with no sugar",
        "sugar_free": True,
    },
    {
        "id": 3,
        "name": "Mango Loco",
        "category": "juice",
        "price": 92.0,
        "stock": 18,
        "flavor_profile": "Tropical mango and mixed fruit profile",
        "sugar_free": False,
    },
    {
        "id": 5,
        "name": "Ultra Paradise",
        "category": "ultra",
        "price": 87.0,
        "stock": 31,
        "flavor_profile": "Bright kiwi and lime-inspired profile with no sugar",
        "sugar_free": True,
    },
    {
        "id": 6,
        "name": "Pacific Punch",
        "category": "punch",
        "price": 95.0,
        "stock": 12,
        "flavor_profile": "Cherry-forward fruit punch profile",
        "sugar_free": False,
    },
    {
        "id": 8,
        "name": "Reserve Orange Dreamsicle",
        "category": "reserve",
        "price": 99.0,
        "stock": 9,
        "flavor_profile": "Orange and vanilla-inspired profile",
        "sugar_free": False,
    },
    {
        "id": 9,
        "name": "Ultra Strawberry Dreams",
        "category": "ultra",
        "price": 91.0,
        "stock": 22,
        "flavor_profile": "Strawberry-inspired profile with a smooth finish",
        "sugar_free": True,
    },
    {
        "id": 10,
        "name": "Ultra Peachy Keen",
        "category": "ultra",
        "price": 90.0,
        "stock": 16,
        "flavor_profile": "Bright peach-inspired profile with no sugar",
        "sugar_free": True,
    },
    {
        "id": 11,
        "name": "Ultra Fiesta Mango",
        "category": "ultra",
        "price": 93.0,
        "stock": 28,
        "flavor_profile": "Juicy mango-inspired profile with a crisp finish",
        "sugar_free": True,
    },
    {
        "id": 13,
        "name": "Khaotic",
        "category": "juice",
        "price": 96.0,
        "stock": 11,
        "flavor_profile": "Orange and tropical fruit-inspired profile",
        "sugar_free": False,
    },
    {
        "id": 14,
        "name": "Aussie Style Lemonade",
        "category": "juice",
        "price": 97.0,
        "stock": 19,
        "flavor_profile": "Tart lemonade-inspired profile with a fresh finish",
        "sugar_free": False,
    },
    {
        "id": 15,
        "name": "Nitro Super Dry",
        "category": "nitro",
        "price": 102.0,
        "stock": 8,
        "flavor_profile": "Smooth citrus profile with a dry sparkling finish",
        "sugar_free": False,
    },
    {
        "id": 16,
        "name": "Nitro Cosmic Peach",
        "category": "nitro",
        "price": 104.0,
        "stock": 13,
        "flavor_profile": "Peach-inspired profile with a soft sparkling finish",
        "sugar_free": False,
    },
    {
        "id": 17,
        "name": "Rehab Tea + Lemonade",
        "category": "rehab",
        "price": 86.0,
        "stock": 20,
        "flavor_profile": "Tea and lemonade-inspired non-carbonated profile",
        "sugar_free": True,
    },
    {
        "id": 18,
        "name": "Reserve White Pineapple",
        "category": "reserve",
        "price": 99.0,
        "stock": 17,
        "flavor_profile": "White pineapple-inspired tropical profile",
        "sugar_free": False,
    },
    {
        "id": 19,
        "name": "Zero Sugar",
        "category": "classic",
        "price": 88.0,
        "stock": 35,
        "flavor_profile": "Classic energy profile with no sugar",
        "sugar_free": True,
    },
    {
        "id": 20,
        "name": "Lo-Carb",
        "category": "classic",
        "price": 86.0,
        "stock": 15,
        "flavor_profile": "Classic profile with a lighter sugar formulation",
        "sugar_free": False,
    },
    {
        "id": 24,
        "name": "Bad Apple",
        "category": "juice",
        "price": 98.0,
        "stock": 26,
        "flavor_profile": "Crisp apple-inspired juice profile",
        "sugar_free": False,
    },
    {
        "id": 26,
        "name": "MIXXD Punch",
        "category": "punch",
        "price": 97.0,
        "stock": 12,
        "flavor_profile": "Cherry and mixed fruit punch profile",
        "sugar_free": False,
    },
    {
        "id": 27,
        "name": "Rio Punch",
        "category": "punch",
        "price": 99.0,
        "stock": 17,
        "flavor_profile": "Papaya, vanilla and blackcurrant-inspired profile",
        "sugar_free": False,
    },
    {
        "id": 29,
        "name": "Reserve Peaches N' Crème",
        "category": "reserve",
        "price": 103.0,
        "stock": 7,
        "flavor_profile": "Peach and cream-inspired reserve profile",
        "sugar_free": False,
    },
    {
        "id": 30,
        "name": "Rehab Peach Tea",
        "category": "rehab",
        "price": 87.0,
        "stock": 23,
        "flavor_profile": "Peach tea-inspired non-carbonated profile",
        "sugar_free": True,
    },
    {
        "id": 31,
        "name": "Rehab Wild Berry Tea",
        "category": "rehab",
        "price": 88.0,
        "stock": 11,
        "flavor_profile": "Wild berry tea-inspired non-carbonated profile",
        "sugar_free": True,
    },
    {
        "id": 34,
        "name": "MAXX Super Dry",
        "category": "nitro",
        "price": 103.0,
        "stock": 12,
        "flavor_profile": "Citrus profile with a smooth nitro-style finish",
        "sugar_free": False,
    },
]

REVIEW_SEED = {
    1: [
        {"user": "Remi", "rating": 5, "date": "2026-06-01"},
        {"user": "Tatelin", "rating": 4, "date": "2026-06-15"},
    ],
    2: [
        {"user": "Marta", "rating": 5, "date": "2026-05-20"},
        {"user": "Noah", "rating": 4, "date": "2026-06-20"},
    ],
    3: [{"user": "Maria", "rating": 5, "date": "2026-05-28"}],
}

USER_SEED = {
    "user_1": {"name": "Remi", "api_key": "energy_remi_123", "role": "user"},
    "user_2": {"name": "Tatelin", "api_key": "energy_tatelin_456", "role": "user"},
    "admin": {"name": "Admin", "api_key": "energy_admin_789", "role": "admin"},
}


class ProductRepository:
    def __init__(self) -> None:
        self._products = deepcopy(PRODUCT_SEED)
        self._reviews = deepcopy(REVIEW_SEED)
        self._next_id = max(cast(int, product["id"]) for product in self._products) + 1

    def list_all(self) -> list[dict[str, Any]]:
        return deepcopy(self._products)

    def get(self, product_id: int) -> dict[str, Any] | None:
        product = next((item for item in self._products if item["id"] == product_id), None)
        return deepcopy(product)

    def add(self, payload: ProductCreate) -> dict[str, Any]:
        product = {"id": self._next_id, **payload.model_dump()}
        self._next_id += 1
        self._products.append(product)
        return deepcopy(product)

    def reviews(self, product_id: int) -> list[dict[str, Any]]:
        return deepcopy(self._reviews.get(product_id, []))


class OrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, OrderRead] = {}
        self._next_id = 1

    def create(self, payload: OrderCreate) -> OrderRead:
        order = OrderRead(
            id=self._next_id,
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
            **payload.model_dump(),
        )
        self._orders[order.id] = order
        self._next_id += 1
        return order.model_copy(deep=True)

    def list_all(self) -> list[OrderRead]:
        return [order.model_copy(deep=True) for order in self._orders.values()]

    def get(self, order_id: int) -> OrderRead | None:
        order = self._orders.get(order_id)
        return order.model_copy(deep=True) if order else None

    def replace(self, order: OrderRead) -> OrderRead:
        self._orders[order.id] = order.model_copy(deep=True)
        return order.model_copy(deep=True)


class NotesRepository:
    def __init__(self) -> None:
        self._notes: dict[int, dict[str, Any]] = {}
        self._next_id = 1

    def create(self, payload: NoteCreate, owner_id: str, author: str) -> dict[str, Any]:
        note = {
            "id": self._next_id,
            "owner_id": owner_id,
            "author": author,
            "created_at": datetime.now(UTC),
            **payload.model_dump(),
        }
        self._notes[self._next_id] = note
        self._next_id += 1
        return deepcopy(note)

    def list_all(self) -> list[dict[str, Any]]:
        return deepcopy(list(self._notes.values()))

    def get(self, note_id: int) -> dict[str, Any] | None:
        note = self._notes.get(note_id)
        return deepcopy(note)

    def delete(self, note_id: int) -> bool:
        return self._notes.pop(note_id, None) is not None

    def count(self) -> int:
        return len(self._notes)


class LinkRepository:
    def __init__(self, code_length: int) -> None:
        self._links: dict[str, dict[str, Any]] = {}
        self._code_length = code_length

    def _generate_code(self) -> str:
        alphabet = ascii_letters + digits
        while True:
            code = "".join(choice(alphabet) for _ in range(self._code_length))
            if code not in self._links:
                return code

    def create(self, payload: LinkCreate) -> dict[str, Any]:
        code = payload.custom_alias or self._generate_code()
        if code in self._links:
            raise ValueError("Alias is already in use")
        link = {
            "short_code": code,
            "original_url": str(payload.original_url),
            "created_at": datetime.now(UTC),
            "clicks": 0,
        }
        self._links[code] = link
        return deepcopy(link)

    def list_all(self) -> list[dict[str, Any]]:
        return deepcopy(list(self._links.values()))

    def resolve(self, code: str) -> dict[str, Any] | None:
        link = self._links.get(code)
        if link is None:
            return None
        link["clicks"] += 1
        return deepcopy(link)

    def delete(self, code: str) -> bool:
        return self._links.pop(code, None) is not None


def paginate[T](items: Iterable[T], skip: int, limit: int) -> list[T]:
    values = list(items)
    return values[skip : skip + limit]
