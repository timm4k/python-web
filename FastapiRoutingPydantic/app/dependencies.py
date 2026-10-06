from typing import Annotated, cast

from fastapi import Depends, Request

from .repositories import LibraryRepository, MeetingRepository


def get_library_repository(request: Request) -> LibraryRepository:
    return cast(LibraryRepository, request.app.state.library_repository)


def get_meeting_repository(request: Request) -> MeetingRepository:
    return cast(MeetingRepository, request.app.state.meeting_repository)


LibraryRepositoryDependency = Annotated[
    LibraryRepository,
    Depends(get_library_repository),
]
MeetingRepositoryDependency = Annotated[
    MeetingRepository,
    Depends(get_meeting_repository),
]
