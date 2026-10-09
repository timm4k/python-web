from collections.abc import AsyncIterator
from typing import cast

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.types import Message, Receive, Scope, Send

from app.database import get_db


def test_transaction_completes_before_response(client: TestClient) -> None:
    application = cast(FastAPI, client.app)
    original_stack = application.middleware_stack
    assert original_stack is not None
    events: list[str] = []

    async def tracked_session(request: Request) -> AsyncIterator[AsyncSession]:
        async for session in get_db(request):
            yield session
        events.append("transaction completed")

    async def tracked_response(scope: Scope, receive: Receive, send: Send) -> None:
        async def record_message(message: Message) -> None:
            if message["type"] == "http.response.start":
                events.append("response started")
            await send(message)

        await original_stack(scope, receive, record_message)

    application.dependency_overrides[get_db] = tracked_session
    application.middleware_stack = tracked_response
    try:
        response = client.post(
            "/users",
            json={"username": "mira_cello", "email": "mira@cadence.example"},
        )
        assert response.status_code == 201
        assert events == ["transaction completed", "response started"]
    finally:
        application.dependency_overrides.pop(get_db)
        application.middleware_stack = original_stack
