from typing import Literal, TypedDict

PerfumeAccent = Literal["violet", "rose", "amber", "blue"]


class Perfume(TypedDict):
    id: int
    name: str
    family: str
    notes: tuple[str, ...]
    price: float
    accent: PerfumeAccent


PERFUMES: tuple[Perfume, ...] = (
    {
        "id": 1,
        "name": "Violet Archive",
        "family": "Powdery floral",
        "notes": ("iris", "violet leaf", "white musk"),
        "price": 2800,
        "accent": "violet",
    },
    {
        "id": 2,
        "name": "Nocturne Rose",
        "family": "Dark floral",
        "notes": ("damask rose", "plum", "incense"),
        "price": 3200,
        "accent": "rose",
    },
    {
        "id": 3,
        "name": "Amber Library",
        "family": "Warm amber",
        "notes": ("benzoin", "vanilla", "sandalwood"),
        "price": 3500,
        "accent": "amber",
    },
    {
        "id": 4,
        "name": "Rain on Glass",
        "family": "Aquatic mineral",
        "notes": ("bergamot", "ozone", "cedar"),
        "price": 2650,
        "accent": "blue",
    },
)
