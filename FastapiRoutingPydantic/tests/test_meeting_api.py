from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

ROOM = {
    "name": "Aurora Room",
    "capacity": 12,
    "floor": 4,
    "has_projector": True,
    "has_whiteboard": True,
}


def create_room(client: TestClient) -> int:
    response = client.post(
        "/api/v1/rooms",
        json=ROOM,
        headers={"X-Admin-Key": "admin-secret-123"},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def booking_payload(
    room_id: int, start: datetime, email: str = "tanya@example.com"
) -> dict[str, object]:
    return {
        "room_id": room_id,
        "user_email": email,
        "start_time": start.isoformat(),
        "end_time": (start + timedelta(hours=2)).isoformat(),
        "purpose": "Architecture workshop",
    }


def test_admin_key_is_required(client: TestClient) -> None:
    assert (
        client.post("/api/v1/rooms", json=ROOM, headers={"X-Admin-Key": "wrong"}).status_code == 403
    )


def test_booking_conflict_availability_and_owner_cancel(client: TestClient) -> None:
    room_id = create_room(client)
    start = datetime.now(UTC) + timedelta(days=2)
    payload = booking_payload(room_id, start)

    first = client.post("/api/v1/bookings", json=payload)
    assert first.status_code == 201
    booking_id = first.json()["id"]

    conflict = booking_payload(room_id, start + timedelta(hours=1), "other@example.com")
    assert client.post("/api/v1/bookings", json=conflict).status_code == 409

    availability = client.get(
        f"/api/v1/rooms/{room_id}/availability",
        params={"date": start.date().isoformat()},
    )
    assert availability.status_code == 200
    assert availability.json()["available"] is False

    forbidden = client.delete(
        f"/api/v1/bookings/{booking_id}",
        headers={"X-User-Email": "other@example.com"},
    )
    assert forbidden.status_code == 403

    cancelled = client.delete(
        f"/api/v1/bookings/{booking_id}",
        headers={"X-User-Email": "tanya@example.com"},
    )
    assert cancelled.status_code == 204
