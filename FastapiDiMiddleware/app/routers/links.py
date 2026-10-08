from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from fastapi.responses import RedirectResponse

from app.dependencies import LinkRepo, log_action, validate_link_admin
from app.errors import LinkNotFoundError
from app.models import LinkCreate, LinkRead

router = APIRouter(tags=["Energy link shortener"])
admin_router = APIRouter(
    prefix="/admin",
    tags=["Link administration"],
    dependencies=[Depends(validate_link_admin), Depends(log_action)],
)


@router.post("/shorten", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
async def shorten_link(payload: LinkCreate, repository: LinkRepo) -> dict[str, object]:
    try:
        return repository.create(payload)
    except ValueError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error


@admin_router.get("/links", response_model=list[LinkRead])
async def list_links(repository: LinkRepo) -> list[dict[str, object]]:
    return repository.list_all()


@admin_router.delete("/links/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: Annotated[str, Path(min_length=1)],
    repository: LinkRepo,
) -> Response:
    if not repository.delete(short_code):
        raise LinkNotFoundError(short_code)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
)
async def follow_link(
    short_code: Annotated[str, Path(min_length=1)],
    repository: LinkRepo,
) -> RedirectResponse:
    link = repository.resolve(short_code)
    if link is None:
        raise LinkNotFoundError(short_code)
    return RedirectResponse(
        str(link["original_url"]),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
