from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.models import Comment, User


def test_create_relational_music_task(
    client: TestClient,
    musical_session: dict[str, int],
) -> None:
    task = client.get(f"/tasks/{musical_session['task_id']}")
    musician = client.get(f"/users/{musical_session['user_id']}")

    assert task.status_code == 200
    assert task.json()["owner_id"] == musical_session["user_id"]
    assert task.json()["owner"]["username"] == "remi_keys"
    assert {tag["name"] for tag in task.json()["tags"]} == {"guitar", "recording"}
    assert musician.status_code == 200
    assert musician.json()["tasks"][0]["title"] == "Track the Midnight Sonata bridge"


def test_filter_update_and_stats(
    client: TestClient,
    musical_session: dict[str, int],
) -> None:
    task_id = musical_session["task_id"]
    user_id = musical_session["user_id"]
    updated = client.patch(
        f"/tasks/{task_id}",
        json={"status": "in_progress", "description": None, "tag_ids": []},
    )
    filtered = client.get("/tasks", params={"status": "in_progress", "offset": 0, "limit": 1})
    stats = client.get(f"/users/{user_id}/tasks/stats")

    assert updated.status_code == 200
    assert updated.json()["description"] is None
    assert updated.json()["tags"] == []
    assert [task["id"] for task in filtered.json()] == [task_id]
    assert stats.json() == {"user_id": user_id, "todo": 0, "in_progress": 1, "done": 0}


def test_missing_relations_and_resources_return_404(client: TestClient) -> None:
    missing_owner = client.post(
        "/tasks",
        json={"title": "Tune the grand piano", "owner_id": 999, "tag_ids": []},
    )
    user = client.post(
        "/users",
        json={"username": "tatelin_strings", "email": "tatelin@cadence.example"},
    ).json()
    missing_tag = client.post(
        "/tasks",
        json={"title": "Tune the grand piano", "owner_id": user["id"], "tag_ids": [999]},
    )

    assert missing_owner.status_code == 404
    assert missing_tag.status_code == 404
    assert client.get("/tasks/999").status_code == 404
    assert client.get("/users/999").status_code == 404


def test_unique_constraints_and_validation(client: TestClient) -> None:
    payload = {"username": "nova_drums", "email": "nova@cadence.example"}
    assert client.post("/users", json=payload).status_code == 201
    assert client.post("/users", json=payload).status_code == 409
    assert client.post("/tags", json={"name": "drums"}).status_code == 201
    assert client.post("/tags", json={"name": "drums"}).status_code == 409
    assert client.get("/tasks", params={"limit": 101}).status_code == 422


def test_delete_task(
    client: TestClient,
    musical_session: dict[str, int],
) -> None:
    task_id = musical_session["task_id"]

    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
    assert client.delete(f"/tasks/{task_id}").status_code == 404


def test_comment_cascade(client: TestClient, musical_session: dict[str, int]) -> None:
    async def add_studio_comment() -> None:
        async with cast(FastAPI, client.app).state.database.session_factory() as db:
            db.add(
                Comment(
                    body="Lift the guitar harmony in bar eight",
                    task_id=musical_session["task_id"],
                    author_id=musical_session["user_id"],
                )
            )
            await db.commit()

    async def count_comments() -> int:
        async with cast(FastAPI, client.app).state.database.session_factory() as db:
            return int(await db.scalar(select(func.count(Comment.id))) or 0)

    assert client.portal is not None
    client.portal.call(add_studio_comment)
    assert client.portal.call(count_comments) == 1
    assert client.delete(f"/tasks/{musical_session['task_id']}").status_code == 204
    assert client.portal.call(count_comments) == 0


def test_active_musicians_only(client: TestClient, musical_session: dict[str, int]) -> None:
    async def deactivate_musician() -> None:
        async with cast(FastAPI, client.app).state.database.session_factory() as db:
            user = await db.get(User, musical_session["user_id"])
            assert user is not None
            user.is_active = False
            await db.commit()

    assert client.portal is not None
    client.portal.call(deactivate_musician)
    assert client.get("/users").json() == []


def test_failed_tag_update_preserves_task(
    client: TestClient, musical_session: dict[str, int]
) -> None:
    task_url = f"/tasks/{musical_session['task_id']}"
    before = client.get(task_url).json()
    assert client.patch(task_url, json={"title": "Wrong take", "tag_ids": [999]}).status_code == 404
    assert client.get(task_url).json() == before


def test_blank_tag_is_rejected(client: TestClient) -> None:
    assert client.post("/tags", json={"name": "   "}).status_code == 422


def test_production_deadline_and_partial_update(
    client: TestClient, musical_session: dict[str, int]
) -> None:
    task_url = f"/tasks/{musical_session['task_id']}"
    original_title = client.get(task_url).json()["title"]
    updated = client.patch(task_url, json={"due_date": "2026-11-14"})
    assert updated.status_code == 200
    assert updated.json()["due_date"] == "2026-11-14"
    assert updated.json()["title"] == original_title
    assert client.patch(task_url, json={"due_date": "2026-13-45"}).status_code == 422
    cleared = client.patch(task_url, json={"due_date": None})
    assert cleared.status_code == 200
    assert cleared.json()["due_date"] is None


def test_invalid_production_filters(client: TestClient) -> None:
    for parameters in ({"offset": -1}, {"limit": 0}, {"status": "recording"}):
        assert client.get("/tasks", params=parameters).status_code == 422
