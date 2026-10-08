from fastapi.testclient import TestClient

from app.repositories import PRODUCT_SEED


def test_product_filters_and_pagination(client: TestClient) -> None:
    response = client.get(
        "/products",
        params={"category": "ultra", "in_stock": "true", "skip": 0, "limit": 2},
    )

    assert response.status_code == 200
    products = response.json()
    assert len(products) == 2
    assert all(
        product["category"] == "ultra" and product["stock"] > 0 for product in products
    )


def test_product_detail_reviews_and_missing_product(client: TestClient) -> None:
    detail = client.get("/products/1")
    reviews = client.get(
        "/products/1/reviews", params={"sort_by": "rating", "order": "asc"}
    )
    missing = client.get("/products/999")

    assert detail.status_code == 200
    assert reviews.status_code == 200
    assert [item["rating"] for item in reviews.json()] == [4, 5]
    assert missing.status_code == 404


def test_create_product_and_read_request_log(client: TestClient) -> None:
    created = client.post(
        "/products",
        json={
            "name": "Ultra Test Lab",
            "category": "ultra",
            "price": 90,
            "stock": 6,
            "flavor_profile": "Test citrus profile",
            "sugar_free": True,
        },
    )
    forbidden = client.get("/admin/requests-log")
    allowed = client.get(
        "/admin/requests-log",
        headers={"X-Admin-Key": "energy-catalog-admin"},
    )

    assert created.status_code == 201
    assert forbidden.status_code == 403
    assert allowed.status_code == 200
    assert any(entry["path"] == "/products" for entry in allowed.json())


def test_created_products_receive_unique_ids(client: TestClient) -> None:
    payload = {
        "name": "Lab Edition",
        "category": "classic",
        "price": 90,
        "stock": 5,
        "flavor_profile": "Limited test profile",
    }
    first = client.post("/products", json=payload).json()
    second = client.post(
        "/products", json={**payload, "name": "Lab Edition Zero"}
    ).json()

    assert first["id"] != second["id"]
    assert first["id"] > max(product["id"] for product in PRODUCT_SEED)
