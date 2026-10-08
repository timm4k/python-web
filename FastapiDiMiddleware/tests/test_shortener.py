from fastapi.testclient import TestClient


def test_create_and_redirect(client: TestClient) -> None:
    response = client.post(
        "/shorten",
        json={"original_url": "https://example.com/energy", "custom_alias": "energy"},
    )
    redirect = client.get("/energy", follow_redirects=False)

    assert response.status_code == 201
    assert redirect.status_code in (302, 307)
    assert redirect.headers["location"] == "https://example.com/energy"
    links = client.get(
        "/admin/links", headers={"X-Admin-Key": "energy-link-admin-2026"}
    )
    assert links.json()[0]["clicks"] == 1


def test_not_found_and_flat_validation_errors(client: TestClient) -> None:
    missing = client.get("/nonexistent")
    invalid = client.post(
        "/shorten",
        json={"original_url": "not-a-url", "custom_alias": "x"},
    )

    assert missing.status_code == 404
    assert missing.json()["error"] == "LINK_NOT_FOUND"
    assert invalid.status_code == 422
    assert set(invalid.json()["errors"]) == {"original_url", "custom_alias"}


def test_admin_protection_delete_and_tracing_headers(client: TestClient) -> None:
    created = client.post(
        "/shorten",
        json={
            "original_url": "https://example.com/admin",
            "custom_alias": "admin-demo",
        },
        headers={"X-Request-ID": "known-request-id"},
    )
    forbidden = client.get("/admin/links")
    allowed = client.get(
        "/admin/links", headers={"X-Admin-Key": "energy-link-admin-2026"}
    )
    deleted = client.delete(
        "/admin/links/admin-demo",
        headers={"X-Admin-Key": "energy-link-admin-2026"},
    )

    assert created.headers["X-Request-ID"] == "known-request-id"
    assert "X-Process-Time" in created.headers
    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert deleted.status_code == 204
