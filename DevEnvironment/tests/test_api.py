from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_page_loads() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Purrfect Python Lab" in response.text


def test_shop_lab_page_and_overview_load() -> None:
    page_response = client.get("/shop-lab")
    overview_response = client.get("/api/shop-lab/overview")
    assert page_response.status_code == 200
    assert "Nine connected exercises" in page_response.text
    assert overview_response.status_code == 200
    assert len(overview_response.json()) == 9


def test_shop_lab_interactive_endpoints() -> None:
    vat_response = client.get("/api/shop-lab/vat", params={"price": 125.50})
    catalog_response = client.get("/api/shop-lab/products")
    order_response = client.post(
        "/api/shop-lab/orders",
        json={"customer_name": "Tate", "product_id": 2},
    )
    simulation_response = client.post("/api/shop-lab/simulate", json={"count": 5})

    assert vat_response.status_code == 200
    assert vat_response.json()["formattedTotal"] == "150.60 UAH"
    assert len(catalog_response.json()) == 3
    assert order_response.status_code == 200
    assert "Feather Wand" in order_response.json()["message"]
    assert len(simulation_response.json()) == 5


def test_shop_lab_order_rejects_unknown_product() -> None:
    response = client.post(
        "/api/shop-lab/orders",
        json={"customer_name": "Tate", "product_id": 999},
    )
    assert response.status_code == 404


def test_environment_uses_virtual_environment() -> None:
    response = client.get("/api/environment")
    assert response.status_code == 200
    assert response.json()["virtualEnvironment"] is True


def test_cat_facts_can_be_filtered_and_sorted() -> None:
    response = client.get(
        "/api/cats",
        params={"category": "anatomy", "keyword": "cat", "sort_by_title": True},
    )
    assert response.status_code == 200
    facts = response.json()
    assert [fact["title"] for fact in facts] == [
        "Built-in compass",
        "High-frequency hearing",
        "Unique nose pattern",
    ]


def test_converter_returns_result() -> None:
    response = client.post(
        "/api/convert",
        json={"value": "255", "from_base": 10, "to_base": 16},
    )
    assert response.status_code == 200
    assert response.json()["result"] == "FF"


def test_converter_rejects_invalid_value() -> None:
    response = client.post(
        "/api/convert",
        json={"value": "102", "from_base": 2, "to_base": 10},
    )
    assert response.status_code == 400
