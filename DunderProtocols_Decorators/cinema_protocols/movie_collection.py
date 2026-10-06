from __future__ import annotations

from collections.abc import Iterator
from types import NotImplementedType

from cinema_protocols.movies import Movie, create_sample_movies


class MovieCollection:
    def __init__(self, movies: list[Movie] | None = None) -> None:
        self._movies: list[Movie] = []
        for movie in movies or []:
            self.add(movie)

    def __repr__(self) -> str:
        return f"MovieCollection(count={len(self)})"

    def __str__(self) -> str:
        if not self:
            return "Movie collection is empty"
        return "\n".join(f"{index}. {movie}" for index, movie in enumerate(self, start=1))

    def __len__(self) -> int:
        return len(self._movies)

    def __bool__(self) -> bool:
        return bool(self._movies)

    def __getitem__(self, index: int) -> Movie:
        return self._movies[index]

    def __contains__(self, item: object) -> bool:
        if isinstance(item, Movie):
            return item in self._movies
        if isinstance(item, str):
            normalized = item.casefold().strip()
            return any(movie.title.casefold() == normalized for movie in self._movies)
        return False

    def __iter__(self) -> Iterator[Movie]:
        return iter(self._movies)

    def __add__(self, other: object) -> MovieCollection | NotImplementedType:
        if not isinstance(other, MovieCollection):
            return NotImplemented
        return MovieCollection([*self, *other])

    def add(self, movie: Movie) -> None:
        if not isinstance(movie, Movie):
            raise TypeError("MovieCollection accepts Movie instances")
        if movie not in self:
            self._movies.append(movie)

    def remove(self, title: str) -> bool:
        normalized = title.casefold().strip()
        for index, movie in enumerate(self._movies):
            if movie.title.casefold() == normalized:
                del self._movies[index]
                return True
        return False

    def top_rated(self, n: int = 3) -> list[Movie]:
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError("Top count must be a non-negative integer")
        return sorted(self._movies, reverse=True)[:n]


def main() -> None:
    movies = create_sample_movies()
    first = MovieCollection(list(movies[:3]))
    second = MovieCollection(list(movies[2:]))
    combined = first + second
    print(f"Collection: {first!r}\n{first}")
    print(f"\nlen: {len(first)}, bool: {bool(first)}")
    print(f"collection[0]: {first[0]}")
    print(f"movie in collection: {movies[0] in first}")
    print(f"'Inception' in collection: {'Inception' in first}")
    print("\nIteration")
    for movie in first:
        print(movie)
    print(f"\nCombined unique movies: {len(combined)}\n{combined}")
    print("\nTop two")
    for movie in combined.top_rated(2):
        print(movie)


if __name__ == "__main__":
    main()
