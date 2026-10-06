from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_page_and_overview() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "Python Protocol Explorer" in response.text
    overview = client.get("/api/overview").json()
    assert len(overview["guides"]) == 5


def test_movie_protocol_results() -> None:
    payload = client.get("/api/movie-protocols").json()
    assert payload["sourceCount"] == 6
    assert payload["setCount"] == 5
    assert payload["sorted"][0].startswith("The Shawshank Redemption")


def test_collection_endpoint() -> None:
    response = client.post("/api/collection", json={"operation": "merge"})
    assert response.status_code == 200
    assert response.json()["method"] == "__add__"
    assert len(response.json()["result"]) == 5


def test_factory_endpoint_preserves_subclass() -> None:
    response = client.post(
        "/api/factory",
        json={
            "source": "csv",
            "premium": True,
            "csv_line": "Dune,2021,Denis Villeneuve,Science fiction,8.0",
        },
    )
    assert response.status_code == 200
    assert response.json()["type"] == "PremiumMovie"


def test_retry_success_and_exhaustion() -> None:
    success = client.post(
        "/api/retry", json={"failures_before_success": 2, "max_attempts": 3}
    ).json()
    exhausted = client.post(
        "/api/retry", json={"failures_before_success": 3, "max_attempts": 2}
    ).json()
    assert success["status"] == "completed"
    assert exhausted["status"] == "exhausted"


def test_session_endpoint() -> None:
    response = client.post("/api/session", json={"movie_indexes": [0, 2]})
    assert response.status_code == 200
    assert response.json()["sameCache"] is True
    assert response.json()["cachedCount"] == 2
