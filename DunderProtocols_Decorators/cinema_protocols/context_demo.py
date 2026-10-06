from __future__ import annotations

import time
from collections.abc import Callable
from functools import update_wrapper
from types import TracebackType
from typing import Any

from cinema_protocols.movies import Movie, create_sample_movies

Reporter = Callable[[str], None]


class Singleton[T]:
    def __init__(self, class_type: type[T]) -> None:
        self._class_type = class_type
        self._instance: T | None = None
        update_wrapper(self, class_type)

    def __call__(self, *args: Any, **kwargs: Any) -> T:
        if self._instance is None:
            self._instance = self._class_type(*args, **kwargs)
        return self._instance


@Singleton
class MovieCache:
    def __init__(self) -> None:
        self._movies: dict[str, Movie] = {}

    def add(self, movie: Movie) -> None:
        self._movies[movie.title.casefold()] = movie

    def get(self, title: str) -> Movie | None:
        return self._movies.get(title.casefold().strip())

    def clear(self) -> None:
        self._movies.clear()

    def __len__(self) -> int:
        return len(self._movies)


class MovieSession:
    def __init__(self, session_name: str, reporter: Reporter = print) -> None:
        normalized_name = session_name.strip()
        if not normalized_name:
            raise ValueError("Session name is required")
        self.session_name = normalized_name
        self._reporter = reporter
        self._movies: list[Movie] = []
        self._started_at: float | None = None

    def __enter__(self) -> MovieSession:
        self._started_at = time.perf_counter()
        self._reporter(f"[Session] '{self.session_name}' started")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        started_at = self._started_at
        elapsed = 0.0 if started_at is None else time.perf_counter() - started_at
        if exc_val is not None:
            self._reporter(f"[Session] Error: {exc_val}")
        self._reporter(
            f"[Session] '{self.session_name}' finished: "
            f"{len(self._movies)} movies in {elapsed:.4f}s"
        )
        self._started_at = None

    def add(self, movie: Movie) -> None:
        if not isinstance(movie, Movie):
            raise TypeError("MovieSession accepts Movie instances")
        self._movies.append(movie)
        self._reporter(f"Added: {movie}")

    def __len__(self) -> int:
        return len(self._movies)

    def __str__(self) -> str:
        return f"MovieSession '{self.session_name}': {len(self)} movies"


def main() -> None:
    movies = create_sample_movies()
    first_cache = MovieCache()
    second_cache = MovieCache()
    first_cache.clear()
    first_cache.add(movies[0])
    print(f"First cache is second cache: {first_cache is second_cache}")
    print(f"Cached movie: {second_cache.get(movies[0].title)}")
    with MovieSession("Evening marathon") as session:
        session.add(movies[0])
        session.add(movies[1])
        print(session)
    try:
        with MovieSession("Interrupted screening") as session:
            session.add(movies[2])
            raise RuntimeError("Projector stopped")
    except RuntimeError as error:
        print(f"Handled outside session: {error}")


if __name__ == "__main__":
    main()
