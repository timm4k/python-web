from fastapi.testclient import TestClient

BOOK = {
    "title": "A Wizard of Earthsea",
    "author": "Ursula K. Le Guin",
    "isbn": "978-0-3953-6080-3",
    "year": 1968,
    "available_copies": 2,
}
USER = {
    "full_name": "Tanya Reader",
    "email": "tanya@example.com",
    "phone": "+380501234567",
}


def test_book_crud_and_filters(client: TestClient) -> None:
    created = client.post("/api/v1/books", json=BOOK)
    assert created.status_code == 201
    book_id = created.json()["id"]

    filtered = client.get("/api/v1/books", params={"author": "Le Guin", "available_only": True})
    assert [book["id"] for book in filtered.json()] == [book_id]

    updated = client.patch(f"/api/v1/books/{book_id}", json={"available_copies": 4})
    assert updated.json()["available_copies"] == 4

    assert client.delete(f"/api/v1/books/{book_id}").status_code == 204
    assert client.get(f"/api/v1/books/{book_id}").status_code == 404


def test_user_me_and_borrowing(client: TestClient) -> None:
    book_id = client.post("/api/v1/books", json=BOOK).json()["id"]
    user_id = client.post("/api/v1/users", json=USER).json()["id"]

    profile = client.get("/api/v1/users/me", headers={"X-User-ID": str(user_id)})
    assert profile.status_code == 200
    assert profile.json()["email"] == USER["email"]

    borrowed = client.post(f"/api/v1/users/{user_id}/borrow/{book_id}", params={"days": 21})
    assert borrowed.status_code == 200
    assert borrowed.json()["days"] == 21


def test_invalid_book_and_phone_return_422(client: TestClient) -> None:
    invalid_book = {**BOOK, "isbn": "wrong"}
    invalid_user = {**USER, "phone": "0501234567"}

    assert client.post("/api/v1/books", json=invalid_book).status_code == 422
    assert client.post("/api/v1/users", json=invalid_user).status_code == 422
