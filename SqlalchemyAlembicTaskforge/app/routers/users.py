from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import DatabaseSession
from app.models import Task, TaskStatus, User
from app.queries import find_user_with_tasks
from app.schemas import TaskStats, UserCreate, UserRead, UserWithTasks

router = APIRouter(prefix="/users", tags=["Musicians"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DatabaseSession) -> User:
    user = User(**payload.model_dump())
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Username or email is already registered",
        ) from error
    await db.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
async def list_active_users(db: DatabaseSession) -> list[User]:
    result = await db.execute(select(User).where(User.is_active.is_(True)).order_by(User.id))
    return list(result.scalars())


@router.get("/{user_id}", response_model=UserWithTasks)
async def get_user(
    user_id: Annotated[int, Path(ge=1)],
    db: DatabaseSession,
) -> User:
    user = await find_user_with_tasks(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Musician was not found")
    return user


@router.get("/{user_id}/tasks/stats", response_model=TaskStats)
async def get_user_task_stats(
    user_id: Annotated[int, Path(ge=1)],
    db: DatabaseSession,
) -> TaskStats:
    if await db.get(User, user_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Musician was not found")
    result = await db.execute(
        select(Task.status, func.count(Task.id))
        .where(Task.owner_id == user_id)
        .group_by(Task.status)
    )
    counts = {task_status: count for task_status, count in result.all()}
    return TaskStats(
        user_id=user_id,
        todo=counts.get(TaskStatus.TODO, 0),
        in_progress=counts.get(TaskStatus.IN_PROGRESS, 0),
        done=counts.get(TaskStatus.DONE, 0),
    )
