from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import TaskStatus


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class OrmSchema(StrictSchema):
    model_config = ConfigDict(from_attributes=True)


class UserCreate(StrictSchema):
    username: str = Field(min_length=2, max_length=50, pattern=r"^[A-Za-z0-9_-]+$")
    email: EmailStr


class UserRead(OrmSchema):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime


class TagCreate(StrictSchema):
    name: str = Field(min_length=2, max_length=50)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class TagRead(OrmSchema):
    id: int
    name: str


class TaskCreate(StrictSchema):
    title: str = Field(min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    priority: int = Field(default=0, ge=0, le=10)
    due_date: date | None = None
    owner_id: int = Field(ge=1)
    tag_ids: list[int] = Field(default_factory=list)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Arrange the bridge for Midnight Sonata",
                "description": "Write the piano voicing and guitar counterline",
                "priority": 8,
                "due_date": "2026-11-14",
                "owner_id": 1,
                "tag_ids": [1, 3],
            }
        },
    )


class TaskUpdate(StrictSchema):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=0, le=10)
    due_date: date | None = None
    tag_ids: list[int] | None = None


class TaskRead(OrmSchema):
    id: int
    owner_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: int
    due_date: date | None
    created_at: datetime
    updated_at: datetime
    owner: UserRead
    tags: list[TagRead]


class TaskSummary(OrmSchema):
    id: int
    title: str
    status: TaskStatus
    priority: int
    due_date: date | None
    tags: list[TagRead]


class UserWithTasks(UserRead):
    tasks: list[TaskSummary]


class TaskStats(StrictSchema):
    user_id: int
    todo: int
    in_progress: int
    done: int
