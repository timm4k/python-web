from typing import Literal

from pydantic import BaseModel, Field


class CollectionRequest(BaseModel):
    operation: Literal["length", "truth", "index", "contains", "iterate", "merge", "top"]
    index: int = 0
    title: str = "Inception"
    count: int = Field(default=3, ge=0, le=10)


class FactoryRequest(BaseModel):
    source: Literal["csv", "dictionary"]
    premium: bool = False
    csv_line: str = "Arrival,2016,Denis Villeneuve,Science fiction,7.9"
    title: str = "Arrival"
    year: int = 2016
    director: str = "Denis Villeneuve"
    genre: str = "Science fiction"
    rating: float = 7.9


class RetryRequest(BaseModel):
    failures_before_success: int = Field(default=2, ge=0, le=5)
    max_attempts: int = Field(default=3, ge=1, le=6)


class SessionRequest(BaseModel):
    movie_indexes: list[int] = Field(default_factory=lambda: [0, 1], max_length=5)
