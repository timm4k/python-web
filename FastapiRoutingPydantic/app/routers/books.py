from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status

from ..dependencies import LibraryRepositoryDependency
from ..models import BookCreate, BookRead, BookUpdate

router = APIRouter(prefix="/books", tags=["Library books"])


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: BookCreate,
    repository: LibraryRepositoryDependency,
) -> BookRead:
    return repository.create_book(payload)


@router.get("", response_model=list[BookRead])
async def list_books(
    repository: LibraryRepositoryDependency,
    author: str | None = None,
    year_from: Annotated[int | None, Query(ge=1800, le=2030)] = None,
    year_to: Annotated[int | None, Query(ge=1800, le=2030)] = None,
    available_only: bool = False,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[BookRead]:
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "year_from cannot exceed year_to")
    return repository.list_books(author, year_from, year_to, available_only, skip, limit)


@router.get("/{book_id}", response_model=BookRead)
async def get_book(book_id: int, repository: LibraryRepositoryDependency) -> BookRead:
    book = repository.get_book(book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


@router.patch("/{book_id}", response_model=BookRead)
async def update_book(
    book_id: int,
    payload: BookUpdate,
    repository: LibraryRepositoryDependency,
) -> BookRead:
    book = repository.update_book(book_id, payload)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int, repository: LibraryRepositoryDependency) -> Response:
    if not repository.delete_book(book_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
