import re
from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

PHONE_PATTERN = re.compile(r"\+380\d{9}")


def validate_phone_number(value: str) -> str:
    if PHONE_PATTERN.fullmatch(value) is None:
        raise ValueError("Phone must match +380XXXXXXXXX")
    return value


def validate_energy_promo(value: str | None) -> str | None:
    if value is not None and not value.startswith("ENERGY"):
        raise ValueError("Promo code must start with ENERGY")
    return value


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductCreate(StrictModel):
    name: str = Field(min_length=1, max_length=100)
    category: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    flavor_profile: str = Field(
        default="Original energy blend", min_length=3, max_length=160
    )
    sugar_free: bool = False


class ProductRead(ProductCreate):
    id: int


class ReviewRead(StrictModel):
    user: str
    rating: int = Field(ge=1, le=5)
    date: str


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemBase(StrictModel):
    product_name: str = Field(min_length=2, max_length=100)
    quantity: int = Field(ge=1, le=99)
    price: float = Field(gt=0)


class OrderCreate(StrictModel):
    customer_name: str = Field(min_length=2, max_length=100)
    customer_phone: str
    delivery_address: str = Field(min_length=10, max_length=300)
    items: list[OrderItemBase] = Field(min_length=1)
    promo_code: str | None = None

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "customer_name": "Tate",
                "customer_phone": "+380501234567",
                "delivery_address": "12 Energy Avenue, Lviv",
                "items": [
                    {"product_name": "Ultra White", "quantity": 2, "price": 85.0},
                    {"product_name": "Mango Loco", "quantity": 1, "price": 92.0},
                ],
                "promo_code": "ENERGYBOOST",
            }
        },
    )

    @field_validator("customer_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return validate_phone_number(value)

    @field_validator("promo_code")
    @classmethod
    def validate_promo_code(cls, value: str | None) -> str | None:
        return validate_energy_promo(value)


class OrderRead(OrderCreate):
    id: int
    status: OrderStatus = OrderStatus.PENDING
    total_price: float = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    @model_validator(mode="after")
    def calculate_total_price(self) -> Self:
        self.total_price = round(
            sum(item.price * item.quantity for item in self.items), 2
        )
        return self


class OrderUpdate(StrictModel):
    customer_name: str | None = Field(default=None, min_length=2, max_length=100)
    customer_phone: str | None = None
    delivery_address: str | None = Field(default=None, min_length=10, max_length=300)
    items: list[OrderItemBase] | None = Field(default=None, min_length=1)
    promo_code: str | None = None
    status: OrderStatus | None = None

    @field_validator("customer_name")
    @classmethod
    def reject_null_customer_name(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Customer name cannot be null")
        return value

    @field_validator("customer_phone")
    @classmethod
    def validate_optional_phone(cls, value: str | None) -> str | None:
        return validate_phone_number(value) if value is not None else None

    @field_validator("promo_code")
    @classmethod
    def validate_optional_promo(cls, value: str | None) -> str | None:
        return validate_energy_promo(value)


class NoteCreate(StrictModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1, max_length=4000)


class NoteRead(NoteCreate):
    id: int
    owner_id: str
    author: str
    created_at: datetime


class UserRead(StrictModel):
    id: str
    name: str
    role: str


class NoteStatsRead(StrictModel):
    total_users: int
    total_notes: int


class LinkCreate(StrictModel):
    original_url: HttpUrl
    custom_alias: str | None = Field(default=None, min_length=3, max_length=64)

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is not None and re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
            raise ValueError(
                "Alias may contain letters, numbers, underscores and hyphens"
            )
        return value


class LinkRead(StrictModel):
    short_code: str
    original_url: str
    created_at: datetime
    clicks: int


class RequestLogRead(StrictModel):
    request_id: str
    method: str
    path: str
    status_code: int
    process_time: str
    timestamp: datetime
