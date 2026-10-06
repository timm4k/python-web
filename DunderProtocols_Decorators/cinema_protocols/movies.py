from functools import total_ordering
from typing import Self


@total_ordering
class Movie:
    def __init__(
        self,
        title: str,
        year: int,
        director: str,
        genre: str,
        rating: float,
    ) -> None:
        self._title = self._require_text(title, "Title")
        self._year = self._require_year(year)
        self._director = self._require_text(director, "Director")
        self._genre = self._require_text(genre, "Genre")
        if not self.validate_rating(rating):
            raise ValueError("Rating must be a number between 0 and 10")
        self._rating = float(rating)

    @property
    def title(self) -> str:
        return self._title

    @property
    def year(self) -> int:
        return self._year

    @property
    def director(self) -> str:
        return self._director

    @property
    def genre(self) -> str:
        return self._genre

    @property
    def rating(self) -> float:
        return self._rating

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(title={self.title!r}, year={self.year}, "
            f"director={self.director!r}, genre={self.genre!r}, rating={self.rating!r})"
        )

    def __str__(self) -> str:
        return f"{self.title} ({self.year}) — {self.rating:.1f} ★"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return (self.title, self.year) == (other.title, other.year)

    def __hash__(self) -> int:
        return hash((self.title, self.year))

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Movie):
            return NotImplemented
        return self.rating < other.rating

    @classmethod
    def from_csv(cls, csv_line: str) -> Self:
        parts = [part.strip() for part in csv_line.split(",")]
        if len(parts) != 5:
            raise ValueError("CSV must contain title, year, director, genre and rating")
        title, raw_year, director, genre, raw_rating = parts
        try:
            return cls(title, int(raw_year), director, genre, float(raw_rating))
        except ValueError as error:
            raise ValueError(f"Invalid movie CSV: {error}") from error

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        required = ("title", "year", "director", "genre", "rating")
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing movie fields: {', '.join(missing)}")
        title = data["title"]
        year = data["year"]
        director = data["director"]
        genre = data["genre"]
        rating = data["rating"]
        if (
            not isinstance(title, str)
            or not isinstance(director, str)
            or not isinstance(genre, str)
        ):
            raise ValueError("Title, director and genre must be strings")
        if isinstance(year, bool) or not isinstance(year, int):
            raise ValueError("Year must be an integer")
        if isinstance(rating, bool) or not isinstance(rating, (int, float)):
            raise ValueError("Rating must be a number")
        return cls(title, year, director, genre, float(rating))

    @staticmethod
    def validate_rating(rating: object) -> bool:
        return (
            not isinstance(rating, bool) and isinstance(rating, (int, float)) and 0 <= rating <= 10
        )

    @staticmethod
    def _require_text(value: str, field: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError(f"{field} is required")
        return normalized

    @staticmethod
    def _require_year(year: int) -> int:
        if isinstance(year, bool) or not isinstance(year, int) or year < 1888:
            raise ValueError("Year must be an integer from 1888 onward")
        return year


def create_sample_movies() -> tuple[Movie, ...]:
    return (
        Movie("Inception", 2010, "Christopher Nolan", "Science fiction", 8.8),
        Movie("The Dark Knight", 2008, "Christopher Nolan", "Crime", 9.0),
        Movie("Interstellar", 2014, "Christopher Nolan", "Science fiction", 8.7),
        Movie(
            "The Shawshank Redemption",
            1994,
            "Frank Darabont",
            "Drama",
            9.3,
        ),
        Movie("Dune", 2021, "Denis Villeneuve", "Science fiction", 8.0),
    )


def main() -> None:
    movies = create_sample_movies()
    for movie in movies:
        print(f"repr: {movie!r}")
        print(f"str:  {movie}")
    print("\nSorted by rating")
    for index, movie in enumerate(sorted(movies, reverse=True), start=1):
        print(f"{index}. {movie}")
    movie_set = set(movies)
    rating_by_movie = {movie: movie.rating for movie in movies[:2]}
    print("\nMovies stored in set")
    for movie in sorted(movie_set, reverse=True):
        print(movie)
    print("\nMovies used as dictionary keys")
    for movie, rating in rating_by_movie.items():
        print(f"{movie.title}: {rating}")


if __name__ == "__main__":
    main()
