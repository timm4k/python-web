from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response, status

from app.database import DatabaseSession
from app.models import Task, TaskStatus, User
from app.queries import find_tags, find_task, task_with_relations
from app.schemas import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Music production tasks"])


def ensure_all_tags_exist(requested_ids: list[int], tags_found: int) -> None:
    if len(set(requested_ids)) != tags_found:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "One or more musical tags were not found")


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: DatabaseSession) -> Task:
    if await db.get(User, payload.owner_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task owner was not found")
    tags = await find_tags(db, payload.tag_ids)
    ensure_all_tags_exist(payload.tag_ids, len(tags))
    values = payload.model_dump(exclude={"tag_ids"})
    task = Task(**values, tags=tags)
    db.add(task)
    await db.flush()
    loaded = await find_task(db, task.id)
    if loaded is None:
        raise RuntimeError("Created task could not be reloaded")
    return loaded


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    db: DatabaseSession,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Task]:
    statement = task_with_relations().order_by(Task.id).offset(offset).limit(limit)
    if task_status is not None:
        statement = statement.where(Task.status == task_status)
    result = await db.execute(statement)
    return list(result.scalars())


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: Annotated[int, Path(ge=1)],
    db: DatabaseSession,
) -> Task:
    task = await find_task(db, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Production task was not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: Annotated[int, Path(ge=1)],
    payload: TaskUpdate,
    db: DatabaseSession,
) -> Task:
    task = await find_task(db, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Production task was not found")
    changes = payload.model_dump(exclude_unset=True)
    tag_ids = changes.pop("tag_ids", None)
    if tag_ids is not None:
        tags = await find_tags(db, tag_ids)
        ensure_all_tags_exist(tag_ids, len(tags))
        task.tags = tags
    nullable_fields = {"description", "due_date"}
    for field, value in changes.items():
        if value is not None or field in nullable_fields:
            setattr(task, field, value)
    await db.flush()
    await db.refresh(task, attribute_names=["updated_at"])
    loaded = await find_task(db, task.id)
    if loaded is None:
        raise RuntimeError("Updated task could not be reloaded")
    return loaded


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: Annotated[int, Path(ge=1)],
    db: DatabaseSession,
) -> Response:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Production task was not found")
    await db.delete(task)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
