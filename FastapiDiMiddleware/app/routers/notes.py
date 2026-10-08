from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    status,
)

from app.dependencies import CurrentUser, NotesRepo, audit_log, get_admin_user
from app.models import NoteCreate, NoteRead, NoteStatsRead, UserRead
from app.repositories import paginate

router = APIRouter(prefix="/api/v1/notes", tags=["Protected flavor notes"])
admin_router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Notes administration"],
    dependencies=[Depends(get_admin_user)],
)


def ensure_note_access(note: dict[str, object], user: dict[str, str]) -> None:
    if user["role"] != "admin" and note["owner_id"] != user["id"]:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "This note belongs to another user"
        )


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(audit_log)],
)
async def create_note(
    payload: NoteCreate,
    user: CurrentUser,
    repository: NotesRepo,
) -> dict[str, object]:
    return repository.create(payload, user["id"], user["name"])


@router.get("", response_model=list[NoteRead])
async def list_notes(
    user: CurrentUser,
    repository: NotesRepo,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
) -> list[dict[str, object]]:
    notes = repository.list_all()
    if user["role"] != "admin":
        notes = [note for note in notes if note["owner_id"] == user["id"]]
    return paginate(notes, skip, limit)


@router.get("/{note_id}", response_model=NoteRead)
async def get_note(
    note_id: Annotated[int, Path(ge=1)],
    user: CurrentUser,
    repository: NotesRepo,
) -> dict[str, object]:
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note was not found")
    ensure_note_access(note, user)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: Annotated[int, Path(ge=1)],
    user: CurrentUser,
    repository: NotesRepo,
) -> Response:
    note = repository.get(note_id)
    if note is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note was not found")
    ensure_note_access(note, user)
    repository.delete(note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@admin_router.get("/users", response_model=list[UserRead])
async def list_all_users(request: Request) -> list[UserRead]:
    return [
        UserRead(id=user_id, name=account["name"], role=account["role"])
        for user_id, account in request.app.state.users.items()
    ]


@admin_router.get("/stats", response_model=NoteStatsRead)
async def get_stats(request: Request, repository: NotesRepo) -> NoteStatsRead:
    return NoteStatsRead(
        total_users=len(request.app.state.users), total_notes=repository.count()
    )
