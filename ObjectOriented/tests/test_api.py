from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_both_technical_pages_load() -> None:
    object_page = client.get("/")
    contracts_page = client.get("/contracts")
    assert object_page.status_code == 200
    assert "Every scent begins as an object" in object_page.text
    assert contracts_page.status_code == 200
    assert "A formula with many layers" in contracts_page.text


def test_both_overviews_contain_nine_modules() -> None:
    object_response = client.get("/api/object-model/overview")
    contracts_response = client.get("/api/contracts/overview")
    assert object_response.status_code == 200
    assert contracts_response.status_code == 200
    assert len(object_response.json()) == 9
    assert len(contracts_response.json()) == 9
    concepts = object_response.json() + contracts_response.json()
    assert all(concept["demonstration"].strip() for concept in concepts)
    assert all(concept["meaning"].strip() for concept in concepts)


def test_perfume_catalog_and_validated_price() -> None:
    catalog_response = client.get("/api/catalog/perfumes")
    price_response = client.post(
        "/api/object-model/price",
        json={
            "name": "Violet Archive",
            "current_price": 2800,
            "new_price": 2400,
        },
    )
    assert len(catalog_response.json()) == 4
    assert price_response.status_code == 200
    assert price_response.json()["accepted"] is True
    assert price_response.json()["formatted"] == "2,400.00 UAH"


def test_price_and_memory_validation() -> None:
    invalid_price = client.post(
        "/api/object-model/price",
        json={
            "name": "Violet Archive",
            "current_price": 2800,
            "new_price": -1,
        },
    )
    invalid_count = client.get("/api/object-model/memory", params={"count": 10})
    assert invalid_price.status_code == 200
    assert invalid_price.json()["accepted"] is False
    assert invalid_price.json()["price"] == 2800
    assert invalid_count.status_code == 422


def test_memory_settings_define_api_limits() -> None:
    response = client.get("/api/object-model/memory-settings")
    assert response.status_code == 200
    assert response.json() == {"minimum": 100, "default": 10_000, "maximum": 25_000}


def test_memory_endpoint_returns_measured_values() -> None:
    response = client.get("/api/object-model/memory", params={"count": 1000})
    payload = response.json()
    assert response.status_code == 200
    assert payload["regularBytes"] > payload["slottedBytes"]
    assert payload["savedPercent"] > 0


def test_mro_polymorphism_and_plugin_formats() -> None:
    mro_response = client.get("/api/contracts/mro")
    vehicles_response = client.get("/api/contracts/polymorphism")
    formats_response = client.get("/api/contracts/formats")
    assert mro_response.json()["diamond"] == ["D", "B", "C", "A", "object"]
    assert len(vehicles_response.json()) == 3
    assert formats_response.json() == ["json", "csv", "yaml"]


def test_export_endpoint_uses_selected_plugin() -> None:
    response = client.post(
        "/api/contracts/export",
        json={
            "name": "Violet Archive",
            "family": "Powdery floral",
            "price": 2800,
            "format": "yaml",
        },
    )
    assert response.status_code == 200
    assert "name: Violet Archive" in response.json()["result"]


def test_export_request_validation() -> None:
    response = client.post(
        "/api/contracts/export",
        json={"name": "", "family": "Floral", "price": -1, "format": "xml"},
    )
    assert response.status_code == 422
