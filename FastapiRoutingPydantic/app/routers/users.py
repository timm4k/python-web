from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, status

from ..dependencies import LibraryRepositoryDependency
from ..models import BorrowingRead, UserCreate, UserRead
from ..settings import settings

router = APIRouter(prefix="/users", tags=["Library users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    repository: LibraryRepositoryDependency,
) -> UserRead:
    return repository.create_user(payload)


@router.get("/me", response_model=UserRead)
async def get_current_user(
    x_user_id: Annotated[int, Header(ge=1)],
    repository: LibraryRepositoryDependency,
) -> UserRead:
    user = repository.get_user(x_user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, repository: LibraryRepositoryDependency) -> UserRead:
    user = repository.get_user(user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.post("/{user_id}/borrow/{book_id}", response_model=BorrowingRead)
async def borrow_book(
    user_id: int,
    book_id: int,
    repository: LibraryRepositoryDependency,
    days: Annotated[int, Query(ge=1, le=settings.max_borrow_days)] = settings.default_borrow_days,
) -> BorrowingRead:
    if not repository.borrow(user_id, book_id):
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "User or available book not found",
        )
    return BorrowingRead(
        user_id=user_id,
        book_id=book_id,
        days=days,
        due_date=date.today() + timedelta(days=days),
    )
