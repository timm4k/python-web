from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status

from app.dependencies import ProductRepo, require_product_admin
from app.models import ProductCreate, ProductRead, RequestLogRead, ReviewRead

router = APIRouter(tags=["Energy catalog"])


@router.get("/products", response_model=list[ProductRead])
async def list_products(
    repository: ProductRepo,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    category: Annotated[str | None, Query(min_length=1)] = None,
    price_min: Annotated[float | None, Query(ge=0)] = None,
    price_max: Annotated[float | None, Query(ge=0)] = None,
    in_stock: bool = False,
) -> list[dict[str, object]]:
    if price_min is not None and price_max is not None and price_min > price_max:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "price_min cannot exceed price_max"
        )
    products = repository.list_all()
    if category is not None:
        products = [item for item in products if item["category"] == category]
    if price_min is not None:
        products = [item for item in products if float(item["price"]) >= price_min]
    if price_max is not None:
        products = [item for item in products if float(item["price"]) <= price_max]
    if in_stock:
        products = [item for item in products if int(item["stock"]) > 0]
    return products[skip : skip + limit]


@router.post(
    "/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED
)
async def create_product(
    payload: ProductCreate, repository: ProductRepo
) -> dict[str, object]:
    return repository.add(payload)


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: Annotated[int, Path(ge=1)],
    repository: ProductRepo,
) -> dict[str, object]:
    product = repository.get(product_id)
    if product is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Product with ID {product_id} was not found",
        )
    return product


@router.get("/products/{product_id}/reviews", response_model=list[ReviewRead])
async def get_product_reviews(
    product_id: Annotated[int, Path(ge=1)],
    repository: ProductRepo,
    sort_by: Literal["date", "rating"] = "date",
    order: Literal["asc", "desc"] = "desc",
) -> list[dict[str, object]]:
    if repository.get(product_id) is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Product with ID {product_id} was not found",
        )
    return sorted(
        repository.reviews(product_id),
        key=lambda review: review[sort_by],
        reverse=order == "desc",
    )


@router.get(
    "/admin/requests-log",
    response_model=list[RequestLogRead],
    dependencies=[Depends(require_product_admin)],
    tags=["Request log"],
)
async def get_request_log(request: Request) -> list[RequestLogRead]:
    return [
        RequestLogRead.model_validate(entry) for entry in request.app.state.request_log
    ]
