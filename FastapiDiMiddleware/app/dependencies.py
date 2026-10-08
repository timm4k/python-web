from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Annotated, cast

from fastapi import Depends, Header, HTTPException, Request, status

from app.repositories import (
    LinkRepository,
    NotesRepository,
    OrderRepository,
    ProductRepository,
)
from app.settings import Settings


def get_settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


def get_product_repository(request: Request) -> ProductRepository:
    return cast(ProductRepository, request.app.state.products)


def get_order_repository(request: Request) -> OrderRepository:
    return cast(OrderRepository, request.app.state.orders)


def get_notes_repository(request: Request) -> NotesRepository:
    return cast(NotesRepository, request.app.state.notes)


def get_link_repository(request: Request) -> LinkRepository:
    return cast(LinkRepository, request.app.state.links)


class APIKeyValidator:
    def __init__(self, required_role: str | None = None) -> None:
        self.required_role = required_role

    def __call__(
        self,
        request: Request,
        x_api_key: Annotated[str, Header()],
    ) -> dict[str, str]:
        for user_id, account in request.app.state.users.items():
            if account["api_key"] != x_api_key:
                continue
            if self.required_role is not None and account["role"] != self.required_role:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN, "Required role is missing"
                )
            return {"id": user_id, "name": account["name"], "role": account["role"]}
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid API key")


class AdminKeyValidator:
    def __call__(
        self,
        settings: Annotated[Settings, Depends(get_settings)],
        x_admin_key: Annotated[str | None, Header()] = None,
    ) -> dict[str, str]:
        if x_admin_key != settings.link_admin_key:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid admin key")
        return {"role": "admin"}


get_current_user = APIKeyValidator()
get_admin_user = APIKeyValidator(required_role="admin")
validate_link_admin = AdminKeyValidator()


async def audit_log(
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> AsyncIterator[None]:
    print(f"[AUDIT] {user['name']} started a protected note operation")
    try:
        yield
    finally:
        print(f"[AUDIT] {user['name']} finished a protected note operation")


async def log_action(
    user: Annotated[dict[str, str], Depends(validate_link_admin)],
) -> AsyncIterator[None]:
    timestamp = datetime.now(UTC).isoformat()
    print(f"[ACTION] {user['role']} started link administration at {timestamp}")
    try:
        yield
    finally:
        print("[ACTION] Link administration operation finished")


def log_user_agent(user_agent: Annotated[str | None, Header()] = None) -> None:
    print(f"[CLIENT] User-Agent: {user_agent or 'unknown'}")


def require_product_admin(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_admin_key != settings.product_admin_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid product admin key")


ProductRepo = Annotated[ProductRepository, Depends(get_product_repository)]
OrderRepo = Annotated[OrderRepository, Depends(get_order_repository)]
NotesRepo = Annotated[NotesRepository, Depends(get_notes_repository)]
LinkRepo = Annotated[LinkRepository, Depends(get_link_repository)]
CurrentUser = Annotated[dict[str, str], Depends(get_current_user)]
