from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from app.database import Base
from app.main import create_app


async def create_test_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture
def client() -> Iterator[TestClient]:
    database_url = "sqlite+aiosqlite:///:memory:"
    application = create_app(database_url)
    with TestClient(application, base_url="http://testserver") as test_client:
        assert test_client.portal is not None
        test_client.portal.call(create_test_schema, application.state.database.engine)
        yield test_client


@pytest.fixture
def musical_session(client: TestClient) -> dict[str, int]:
    user = client.post(
        "/users",
        json={"username": "remi_keys", "email": "remi@cadence.example"},
    ).json()
    guitar = client.post("/tags", json={"name": "guitar"}).json()
    recording = client.post("/tags", json={"name": "recording"}).json()
    task = client.post(
        "/tasks",
        json={
            "title": "Track the Midnight Sonata bridge",
            "description": "Record the guitar counterline over the piano voicing",
            "priority": 8,
            "due_date": "2026-11-14",
            "owner_id": user["id"],
            "tag_ids": [guitar["id"], recording["id"]],
        },
    ).json()
    return {
        "user_id": user["id"],
        "guitar_id": guitar["id"],
        "recording_id": recording["id"],
        "task_id": task["id"],
    }
