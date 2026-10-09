from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import DatabaseSession
from app.models import Tag
from app.schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["Musical tags"])


@router.post("", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(payload: TagCreate, db: DatabaseSession) -> Tag:
    tag = Tag(name=payload.name)
    db.add(tag)
    try:
        await db.flush()
    except IntegrityError as error:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Tag already exists") from error
    await db.refresh(tag)
    return tag


@router.get("", response_model=list[TagRead])
async def list_tags(db: DatabaseSession) -> list[Tag]:
    result = await db.execute(select(Tag).order_by(Tag.name))
    return list(result.scalars())
