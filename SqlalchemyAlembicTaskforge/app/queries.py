from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Tag, Task, User


def task_with_relations() -> Select[tuple[Task]]:
    return select(Task).options(selectinload(Task.owner), selectinload(Task.tags))


async def find_task(session: AsyncSession, task_id: int) -> Task | None:
    result = await session.execute(task_with_relations().where(Task.id == task_id))
    return result.scalar_one_or_none()


async def find_tags(session: AsyncSession, tag_ids: list[int]) -> list[Tag]:
    unique_ids = set(tag_ids)
    if not unique_ids:
        return []
    result = await session.execute(select(Tag).where(Tag.id.in_(unique_ids)))
    return list(result.scalars())


async def find_user_with_tasks(session: AsyncSession, user_id: int) -> User | None:
    statement = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.tasks).selectinload(Task.tags))
    )
    result = await session.execute(statement)
    return result.scalar_one_or_none()
