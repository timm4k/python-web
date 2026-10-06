from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Query, Response, status

from ..dependencies import MeetingRepositoryDependency
from ..models import BookingCreate, BookingRead
from ..settings import settings

router = APIRouter(prefix="/bookings", tags=["Room bookings"])


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    repository: MeetingRepositoryDependency,
) -> BookingRead:
    if repository.get_room(payload.room_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    if repository.has_conflict(payload.room_id, payload.start_time, payload.end_time):
        raise HTTPException(status.HTTP_409_CONFLICT, "Room is already booked for this time")
    if (
        repository.active_booking_count(str(payload.user_email), datetime.now(UTC))
        >= settings.max_active_bookings
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, "User already has three active bookings")
    return repository.create_booking(payload)


@router.get("", response_model=list[BookingRead])
async def list_bookings(
    repository: MeetingRepositoryDependency,
    room_id: Annotated[int | None, Query(ge=1)] = None,
    user_email: str | None = None,
) -> list[BookingRead]:
    return repository.list_bookings(room_id, user_email)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: int,
    x_user_email: Annotated[str, Header()],
    repository: MeetingRepositoryDependency,
) -> Response:
    result = repository.delete_booking(booking_id, x_user_email)
    if result is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Booking not found")
    if result is False:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the booking owner can cancel")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
