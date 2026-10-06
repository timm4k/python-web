from collections.abc import Iterable
from datetime import date, datetime

from .models import (
    BookCreate,
    BookingCreate,
    BookingRead,
    BookRead,
    BookUpdate,
    RoomCreate,
    RoomRead,
    UserCreate,
    UserRead,
)


class LibraryRepository:
    def __init__(self) -> None:
        self._books: dict[int, BookRead] = {}
        self._users: dict[int, UserRead] = {}
        self._next_book_id = 1
        self._next_user_id = 1

    def create_book(self, payload: BookCreate) -> BookRead:
        book = BookRead(id=self._next_book_id, **payload.model_dump())
        self._books[book.id] = book
        self._next_book_id += 1
        return book

    def list_books(
        self,
        author: str | None,
        year_from: int | None,
        year_to: int | None,
        available_only: bool,
        skip: int,
        limit: int,
    ) -> list[BookRead]:
        books: Iterable[BookRead] = self._books.values()
        if author:
            books = (book for book in books if author.casefold() in book.author.casefold())
        if year_from is not None:
            books = (book for book in books if book.year >= year_from)
        if year_to is not None:
            books = (book for book in books if book.year <= year_to)
        if available_only:
            books = (book for book in books if book.available_copies > 0)
        return list(books)[skip : skip + limit]

    def get_book(self, book_id: int) -> BookRead | None:
        return self._books.get(book_id)

    def update_book(self, book_id: int, payload: BookUpdate) -> BookRead | None:
        book = self.get_book(book_id)
        if book is None:
            return None
        updated = book.model_copy(update=payload.model_dump(exclude_unset=True))
        self._books[book_id] = updated
        return updated

    def delete_book(self, book_id: int) -> bool:
        return self._books.pop(book_id, None) is not None

    def create_user(self, payload: UserCreate) -> UserRead:
        user = UserRead(id=self._next_user_id, **payload.model_dump(), borrowed_books=[])
        self._users[user.id] = user
        self._next_user_id += 1
        return user

    def get_user(self, user_id: int) -> UserRead | None:
        return self._users.get(user_id)

    def borrow(self, user_id: int, book_id: int) -> bool:
        user = self.get_user(user_id)
        book = self.get_book(book_id)
        if user is None or book is None or book.available_copies == 0:
            return False
        user = user.model_copy(update={"borrowed_books": [*user.borrowed_books, book_id]})
        book = book.model_copy(update={"available_copies": book.available_copies - 1})
        self._users[user_id] = user
        self._books[book_id] = book
        return True


class MeetingRepository:
    def __init__(self) -> None:
        self._rooms: dict[int, RoomRead] = {}
        self._bookings: dict[int, BookingRead] = {}
        self._next_room_id = 1
        self._next_booking_id = 1

    def create_room(self, payload: RoomCreate) -> RoomRead:
        room = RoomRead(id=self._next_room_id, **payload.model_dump())
        self._rooms[room.id] = room
        self._next_room_id += 1
        return room

    def list_rooms(
        self,
        min_capacity: int | None,
        floor: int | None,
        has_projector: bool | None,
    ) -> list[RoomRead]:
        rooms: Iterable[RoomRead] = self._rooms.values()
        if min_capacity is not None:
            rooms = (room for room in rooms if room.capacity >= min_capacity)
        if floor is not None:
            rooms = (room for room in rooms if room.floor == floor)
        if has_projector is not None:
            rooms = (room for room in rooms if room.has_projector is has_projector)
        return list(rooms)

    def get_room(self, room_id: int) -> RoomRead | None:
        return self._rooms.get(room_id)

    def create_booking(self, payload: BookingCreate) -> BookingRead:
        booking = BookingRead(id=self._next_booking_id, **payload.model_dump())
        self._bookings[booking.id] = booking
        self._next_booking_id += 1
        return booking

    def list_bookings(
        self,
        room_id: int | None = None,
        user_email: str | None = None,
    ) -> list[BookingRead]:
        bookings: Iterable[BookingRead] = self._bookings.values()
        if room_id is not None:
            bookings = (booking for booking in bookings if booking.room_id == room_id)
        if user_email:
            bookings = (
                booking
                for booking in bookings
                if str(booking.user_email).casefold() == user_email.casefold()
            )
        return list(bookings)

    def has_conflict(self, room_id: int, start_time: datetime, end_time: datetime) -> bool:
        return any(
            start_time < booking.end_time and end_time > booking.start_time
            for booking in self.list_bookings(room_id=room_id)
        )

    def active_booking_count(self, user_email: str, now: datetime) -> int:
        return sum(booking.end_time > now for booking in self.list_bookings(user_email=user_email))

    def bookings_on_date(self, room_id: int, target_date: date) -> list[BookingRead]:
        return [
            booking
            for booking in self.list_bookings(room_id=room_id)
            if booking.start_time.date() == target_date
        ]

    def delete_booking(self, booking_id: int, user_email: str) -> bool | None:
        booking = self._bookings.get(booking_id)
        if booking is None:
            return None
        if str(booking.user_email).casefold() != user_email.casefold():
            return False
        del self._bookings[booking_id]
        return True
