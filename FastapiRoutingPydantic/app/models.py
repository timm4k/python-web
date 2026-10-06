from datetime import UTC, date, datetime, timedelta
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

ISBN_PATTERN = r"^\d{3}-\d-\d{4}-\d{4}-\d$"
PHONE_PATTERN = r"^\+380\d{9}$"


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BookCreate(ApiModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    isbn: str = Field(pattern=ISBN_PATTERN)
    year: int = Field(ge=1800, le=2030)
    available_copies: int = Field(ge=0)


class BookRead(BookCreate):
    id: int


class BookUpdate(ApiModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    isbn: str | None = Field(default=None, pattern=ISBN_PATTERN)
    year: int | None = Field(default=None, ge=1800, le=2030)
    available_copies: int | None = Field(default=None, ge=0)


class UserCreate(ApiModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(pattern=PHONE_PATTERN)


class UserRead(UserCreate):
    id: int
    borrowed_books: list[int] = Field(default_factory=list)


class BorrowingRead(ApiModel):
    user_id: int
    book_id: int
    days: int
    due_date: date


class RoomCreate(ApiModel):
    name: str = Field(min_length=3, max_length=50)
    capacity: int = Field(ge=2, le=100)
    floor: int = Field(ge=1, le=20)
    has_projector: bool = False
    has_whiteboard: bool = False


class RoomRead(RoomCreate):
    id: int


class BookingCreate(ApiModel):
    room_id: int = Field(ge=1)
    user_email: EmailStr
    start_time: datetime
    end_time: datetime
    purpose: str = Field(min_length=5, max_length=200)

    @field_validator("start_time")
    @classmethod
    def start_must_be_future(cls, value: datetime) -> datetime:
        normalized = value if value.tzinfo else value.replace(tzinfo=UTC)
        if normalized <= datetime.now(UTC):
            raise ValueError("start_time must be in the future")
        return normalized

    @field_validator("end_time")
    @classmethod
    def normalize_end_time(cls, value: datetime) -> datetime:
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    @model_validator(mode="after")
    def validate_time_range(self) -> Self:
        duration = self.end_time - self.start_time
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        if not timedelta(minutes=30) <= duration <= timedelta(hours=8):
            raise ValueError("booking duration must be between 30 minutes and 8 hours")
        return self


class BookingRead(BookingCreate):
    id: int


class AvailabilityRead(ApiModel):
    room_id: int
    date: date
    available: bool
    bookings: list[BookingRead]
