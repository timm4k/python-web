from datetime import date
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, status

from ..dependencies import MeetingRepositoryDependency
from ..models import AvailabilityRead, RoomCreate, RoomRead
from ..settings import settings

router = APIRouter(prefix="/rooms", tags=["Meeting rooms"])


@router.get("", response_model=list[RoomRead])
async def list_rooms(
    repository: MeetingRepositoryDependency,
    min_capacity: Annotated[int | None, Query(ge=2, le=100)] = None,
    floor: Annotated[int | None, Query(ge=1, le=20)] = None,
    has_projector: bool | None = None,
) -> list[RoomRead]:
    return repository.list_rooms(min_capacity, floor, has_projector)


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(
    payload: RoomCreate,
    x_admin_key: Annotated[str, Header()],
    repository: MeetingRepositoryDependency,
) -> RoomRead:
    if x_admin_key != settings.admin_key:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid admin key")
    return repository.create_room(payload)


@router.get("/{room_id}", response_model=RoomRead)
async def get_room(room_id: int, repository: MeetingRepositoryDependency) -> RoomRead:
    room = repository.get_room(room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.get("/{room_id}/availability", response_model=AvailabilityRead)
async def get_availability(
    room_id: int,
    target_date: Annotated[date, Query(alias="date")],
    repository: MeetingRepositoryDependency,
) -> AvailabilityRead:
    if repository.get_room(room_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    bookings = repository.bookings_on_date(room_id, target_date)
    return AvailabilityRead(
        room_id=room_id,
        date=target_date,
        available=not bookings,
        bookings=bookings,
    )
