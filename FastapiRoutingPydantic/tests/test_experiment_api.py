from copy import deepcopy

from fastapi.testclient import TestClient

from app.service_config import VALID_CONFIG


def test_grouping_endpoint_explains_each_strategy(client: TestClient) -> None:
    collected = client.get(
        "/api/v1/experiments/task-grouping",
        params={"strategy": "gather-collect"},
    )
    grouped = client.get(
        "/api/v1/experiments/task-grouping",
        params={"strategy": "task-group"},
    )

    assert collected.status_code == 200
    assert collected.json()["completed"] == 4
    assert collected.json()["errors"] == 1
    assert grouped.status_code == 200
    assert grouped.json()["errors"] == 1
    assert grouped.json()["completed"] + grouped.json()["cancelled"] == 4


def test_config_endpoint_normalizes_production_debug(client: TestClient) -> None:
    payload = deepcopy(VALID_CONFIG)
    payload["debug_mode"] = True

    response = client.post("/api/v1/experiments/validate-config", json=payload)

    assert response.status_code == 200
    assert response.json()["debug_mode"] is False
    assert response.json()["masked_secret"] == "**********"


def test_config_endpoint_returns_422_for_invalid_configuration(
    client: TestClient,
) -> None:
    payload = deepcopy(VALID_CONFIG)
    payload["admin_emails"] = ["invalid"]
    payload["secret_key"] = "short"

    response = client.post("/api/v1/experiments/validate-config", json=payload)

    assert response.status_code == 422


def test_openapi_contains_assignment_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]

    assert "/api/v1/benchmark/cpu-bound-sync" in paths
    assert "/api/v1/benchmark/cpu-bound-async" in paths
    assert "/api/v1/books/{book_id}" in paths
    assert "/api/v1/users/me" in paths
    assert "/api/v1/rooms/{room_id}/availability" in paths
    assert "/api/v1/bookings/{booking_id}" in paths
