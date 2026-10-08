from fastapi.testclient import TestClient

ORDER = {
    "customer_name": "Tate",
    "customer_phone": "+380501234567",
    "delivery_address": "12 Energy Avenue, Lviv",
    "items": [{"product_name": "Ultra White", "quantity": 2, "price": 85}],
    "promo_code": "ENERGYBOOST",
}


def test_create_filter_and_partially_update_order(client: TestClient) -> None:
    created = client.post("/api/v1/orders", json=ORDER)
    listed = client.get("/api/v1/orders", params={"status": "pending"})
    updated = client.patch(
        f"/api/v1/orders/{created.json()['id']}",
        json={"status": "confirmed"},
    )

    assert created.status_code == 201
    assert created.json()["total_price"] == 170
    assert len(listed.json()) == 1
    assert updated.json()["customer_name"] == ORDER["customer_name"]
    assert updated.json()["status"] == "confirmed"


def test_final_order_status_and_validation(client: TestClient) -> None:
    created = client.post("/api/v1/orders", json=ORDER).json()
    delivered = client.patch(
        f"/api/v1/orders/{created['id']}", json={"status": "delivered"}
    )
    rejected = client.patch(
        f"/api/v1/orders/{created['id']}", json={"status": "pending"}
    )
    null_name = client.patch(
        f"/api/v1/orders/{created['id']}", json={"customer_name": None}
    )
    invalid_promo = client.post(
        "/api/v1/orders",
        json={**ORDER, "promo_code": "BOOSTONLY"},
    )

    assert delivered.status_code == 200
    assert rejected.status_code == 400
    assert null_name.status_code == 422
    assert invalid_promo.status_code == 422


def test_item_patch_is_revalidated_and_recalculates_total(client: TestClient) -> None:
    created = client.post("/api/v1/orders", json=ORDER).json()
    updated = client.patch(
        f"/api/v1/orders/{created['id']}",
        json={"items": [{"product_name": "Mango Loco", "quantity": 3, "price": 92}]},
    )

    assert updated.status_code == 200
    assert updated.json()["total_price"] == 276
