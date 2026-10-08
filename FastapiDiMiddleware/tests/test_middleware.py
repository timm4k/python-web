from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def test_cors_and_trusted_host() -> None:
    application = create_app(Settings(rate_limit=20))
    with TestClient(application, base_url="http://localhost") as client:
        cors = client.options(
            "/products",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        untrusted = client.get("/products", headers={"Host": "untrusted.example"})

    assert cors.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert untrusted.status_code == 400


def test_rate_limiter_returns_429() -> None:
    application = create_app(Settings(rate_limit=2, rate_window_seconds=60))
    with TestClient(application, base_url="http://localhost") as client:
        assert client.get("/missing-one").status_code == 404
        assert client.get("/missing-two").status_code == 404
        limited = client.get("/missing-three")

    assert limited.status_code == 429
    assert limited.json()["error"] == "RATE_LIMITED"
    assert "X-Request-ID" in limited.headers
    assert "X-Process-Time" in limited.headers


def test_catalog_and_orders_do_not_consume_shortener_limit() -> None:
    application = create_app(Settings(rate_limit=1, rate_window_seconds=60))
    with TestClient(application, base_url="http://localhost") as client:
        assert client.get("/products").status_code == 200
        assert client.get("/products").status_code == 200
        order = client.post(
            "/api/v1/orders",
            json={
                "customer_name": "Tate",
                "customer_phone": "+380501234567",
                "delivery_address": "12 Energy Avenue, Lviv",
                "items": [
                    {"product_name": "Original Green", "quantity": 2, "price": 89}
                ],
                "promo_code": "ENERGYBOOST",
            },
        )

    assert order.status_code == 201
