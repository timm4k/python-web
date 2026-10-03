from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.concepts import ConceptSummary, build_concepts
from object_model.products import Product
from object_model.slots_perf import RegularPoint, SlottedPoint, measure_peak_memory

router = APIRouter(prefix="/api/object-model", tags=["Object Model"])


class PriceRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    current_price: float = Field(ge=0)
    new_price: int | float | str


OBJECT_CONCEPTS = build_concepts(
    "object_model",
    (
        (
            "library",
            "Instances",
            "State, behavior and developer representation",
            "Creates three Book objects, prints their repr and changes one price with a method",
            "Every instance keeps its own data while all instances share the class behavior",
        ),
        (
            "teams",
            "Attribute ownership",
            "Class state versus instance state",
            "Compares one shared class list with separate lists created inside __init__",
            "Mutable class attributes are shared, while instance attributes belong to one object",
        ),
        (
            "calculator",
            "Method binding",
            "Bound and unbound calls",
            "Calls add through an object and through Calculator while passing "
            "the object explicitly",
            "A bound method supplies self automatically; the class function does not",
        ),
        (
            "object_lifecycle",
            "Object lifecycle",
            "Allocation with __new__ and initialization",
            "Prints the order of __new__ and __init__ and reproduces an invalid __init__ return",
            "__new__ creates the object first; __init__ configures it and must return None",
        ),
        (
            "config",
            "Singleton",
            "Single configuration identity",
            "Creates AppSettings twice with different values and compares object identity",
            "__new__ returns the existing instance, so later construction cannot replace its state",
        ),
        (
            "slots_perf",
            "Memory layout",
            "__slots__ and measured allocations",
            "Measures regular and slotted point collections and tries to add a dynamic attribute",
            "Slots remove each instance dictionary, save memory and restrict available attributes",
        ),
        (
            "vault",
            "Encapsulation",
            "Access conventions and name mangling",
            "Reads public and protected values, then demonstrates direct and "
            "mangled private access",
            "Underscores communicate intended access; name mangling prevents accidental collisions",
        ),
        (
            "products",
            "Properties",
            "Validated accessors and protected storage",
            "Assigns valid, negative and text prices through the same public attribute",
            "A property preserves a simple interface while controlling writes to internal state",
        ),
        (
            "car_model",
            "Descriptors",
            "Reusable numeric field validation",
            "Uses one NonNegativeNumber descriptor for mileage and fuel capacity",
            "Descriptors centralize field behavior so multiple attributes "
            "reuse one validation rule",
        ),
    ),
)

MIN_MEMORY_OBJECTS = 100
DEFAULT_MEMORY_OBJECTS = 10_000
MAX_MEMORY_OBJECTS = 25_000


@router.get("/overview")
def overview() -> tuple[ConceptSummary, ...]:
    return OBJECT_CONCEPTS


@router.get("/memory-settings")
def memory_settings() -> dict[str, int]:
    return {
        "minimum": MIN_MEMORY_OBJECTS,
        "default": DEFAULT_MEMORY_OBJECTS,
        "maximum": MAX_MEMORY_OBJECTS,
    }


@router.post("/price")
def validate_price(request: PriceRequest) -> dict[str, str | float | bool]:
    product = Product(request.name, request.current_price)
    try:
        product.price = request.new_price
    except (TypeError, ValueError) as error:
        return {
            "accepted": False,
            "name": product.name,
            "price": product.price,
            "formatted": f"{product.price:,.2f} UAH",
            "message": str(error),
        }
    return {
        "accepted": True,
        "name": product.name,
        "price": product.price,
        "formatted": f"{product.price:,.2f} UAH",
        "message": "The setter accepted the value and updated protected storage",
    }


@router.get("/memory")
def memory_comparison(
    count: int = Query(
        default=DEFAULT_MEMORY_OBJECTS,
        ge=MIN_MEMORY_OBJECTS,
        le=MAX_MEMORY_OBJECTS,
    ),
) -> dict[str, int | float]:
    regular_peak = measure_peak_memory(RegularPoint, count)
    slotted_peak = measure_peak_memory(SlottedPoint, count)
    saved_percent = round((1 - slotted_peak / regular_peak) * 100, 1)
    return {
        "count": count,
        "regularBytes": regular_peak,
        "slottedBytes": slotted_peak,
        "savedPercent": saved_percent,
    }
