from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user
from app.main import create_app
from app.settings import Settings


def test_note_ownership_and_admin_visibility(client: TestClient) -> None:
    created = client.post(
        "/api/v1/notes",
        headers={"X-API-Key": "energy_remi_123"},
        json={"title": "Ultra", "content": "Citrus profile"},
    )
    forbidden = client.get(
        "/api/v1/notes/1", headers={"X-API-Key": "energy_tatelin_456"}
    )
    admin_list = client.get("/api/v1/notes", headers={"X-API-Key": "energy_admin_789"})

    assert created.status_code == 201
    assert created.json()["owner_id"] == "user_1"
    assert forbidden.status_code == 403
    assert len(admin_list.json()) == 1


def test_admin_router_uses_global_role_dependency(client: TestClient) -> None:
    forbidden = client.get(
        "/api/v1/admin/users", headers={"X-API-Key": "energy_remi_123"}
    )
    allowed = client.get(
        "/api/v1/admin/stats", headers={"X-API-Key": "energy_admin_789"}
    )

    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["total_users"] == 3


def test_owner_can_delete_note(client: TestClient) -> None:
    headers = {"X-API-Key": "energy_remi_123"}
    created = client.post(
        "/api/v1/notes",
        headers=headers,
        json={"title": "Reserve", "content": "Orange profile"},
    ).json()
    deleted = client.delete(f"/api/v1/notes/{created['id']}", headers=headers)
    missing = client.get(f"/api/v1/notes/{created['id']}", headers=headers)

    assert deleted.status_code == 204
    assert missing.status_code == 404


@pytest.fixture
def override_client() -> Iterator[TestClient]:
    application = create_app(Settings(rate_limit=200))
    application.dependency_overrides[get_current_user] = lambda: {
        "id": "test_user",
        "name": "Test",
        "role": "user",
    }
    with TestClient(application, base_url="http://localhost") as test_client:
        yield test_client
    application.dependency_overrides.clear()


def test_current_user_dependency_can_be_overridden(override_client: TestClient) -> None:
    response = override_client.post(
        "/api/v1/notes",
        json={"title": "Test", "content": "Dependency override"},
    )

    assert response.status_code == 201
    assert response.json()["author"] == "Test"
