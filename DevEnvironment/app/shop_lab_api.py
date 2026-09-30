from typing import TypedDict

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from shop_lab.module_lab import utilities
from shop_lab.order_simulator import OrderRecord, generate_orders
from shop_lab.shop.catalog import Product, products
from shop_lab.shop.orders.processing import build_order_message

router = APIRouter(prefix="/api/shop-lab", tags=["Shop Lab"])


class TaskSummary(TypedDict):
    number: int
    title: str
    concept: str
    command: str


class OrderRequest(BaseModel):
    customer_name: str = Field(min_length=1, max_length=60)
    product_id: int = Field(gt=0)


class SimulationRequest(BaseModel):
    count: int = Field(default=5, ge=1, le=10)


TASKS: tuple[TaskSummary, ...] = (
    {
        "number": 1,
        "title": "Custom module",
        "concept": "Three import styles",
        "command": "python -m shop_lab.module_lab.app",
    },
    {
        "number": 2,
        "title": "Import inspector",
        "concept": "sys.path and sys.modules",
        "command": "python -m shop_lab.module_lab.inspector",
    },
    {
        "number": 3,
        "title": "Entry point",
        "concept": "__name__ and reusable modules",
        "command": "python -m shop_lab.module_lab.math_ops",
    },
    {
        "number": 4,
        "title": "Import design",
        "concept": "Broken and fixed dependency flow",
        "command": "python -m shop_lab.circular_import.showcase",
    },
    {
        "number": 5,
        "title": "Shop package",
        "concept": "Catalog and customers",
        "command": "python -m shop_lab.main",
    },
    {
        "number": 6,
        "title": "Relative imports",
        "concept": "Package-aware order processing",
        "command": "python -m shop_lab.main",
    },
    {
        "number": 7,
        "title": "Package facade",
        "concept": "__init__, __all__ and version",
        "command": "python -m shop_lab.main",
    },
    {
        "number": 8,
        "title": "Isolated client",
        "concept": "venv and requirements",
        "command": (
            "shop_lab\\http_client\\.venv\\Scripts\\python shop_lab\\http_client\\fetch_api.py"
        ),
    },
    {
        "number": 9,
        "title": "Order simulator",
        "concept": "random, datetime and JSON",
        "command": "python -m shop_lab.order_simulator",
    },
)


@router.get("/overview")
async def overview() -> tuple[TaskSummary, ...]:
    return TASKS


@router.get("/vat")
async def vat_calculation(
    price: float = Query(ge=0, le=1_000_000),
) -> dict[str, float | str]:
    try:
        vat = utilities.calculate_vat(price)
        total = price + vat
        return {
            "price": price,
            "vat": vat,
            "total": total,
            "formattedVat": utilities.format_currency(vat),
            "formattedTotal": utilities.format_currency(total),
        }
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/products")
async def catalog() -> list[Product]:
    return list(products)


@router.post("/orders")
async def create_shop_order(request: OrderRequest) -> dict[str, str]:
    try:
        message = build_order_message(request.customer_name, request.product_id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {"message": message}


@router.post("/simulate")
async def simulate_orders(request: SimulationRequest) -> list[OrderRecord]:
    return generate_orders(request.count)
