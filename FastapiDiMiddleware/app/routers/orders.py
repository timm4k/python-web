from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from app.dependencies import OrderRepo
from app.models import OrderCreate, OrderRead, OrderStatus, OrderUpdate
from app.repositories import paginate

router = APIRouter(prefix="/api/v1/orders", tags=["Energy orders"])
FINAL_STATUSES = frozenset({OrderStatus.DELIVERED, OrderStatus.CANCELLED})


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(payload: OrderCreate, repository: OrderRepo) -> OrderRead:
    return repository.create(payload)


@router.get("", response_model=list[OrderRead])
async def list_orders(
    repository: OrderRepo,
    order_status: Annotated[OrderStatus | None, Query(alias="status")] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[OrderRead]:
    orders = repository.list_all()
    if order_status is not None:
        orders = [order for order in orders if order.status is order_status]
    return paginate(orders, skip, limit)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: Annotated[int, Path(ge=1)],
    repository: OrderRepo,
) -> OrderRead:
    order = repository.get(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order was not found")
    return order


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: Annotated[int, Path(ge=1)],
    payload: OrderUpdate,
    repository: OrderRepo,
) -> OrderRead:
    order = repository.get(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Order was not found")
    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and order.status in FINAL_STATUSES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Final order status cannot be changed"
        )
    applicable_changes = {
        field: value
        for field, value in changes.items()
        if value is not None or field == "promo_code"
    }
    updated_data = {**order.model_dump(), **applicable_changes}
    return repository.replace(OrderRead.model_validate(updated_data))
