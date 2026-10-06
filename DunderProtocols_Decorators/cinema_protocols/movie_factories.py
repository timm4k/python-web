from cinema_protocols.movies import Movie


class PremiumMovie(Movie):
    def __init__(
        self,
        title: str,
        year: int,
        director: str,
        genre: str,
        rating: float,
        exclusive: bool = True,
    ) -> None:
        super().__init__(title, year, director, genre, rating)
        self.exclusive = exclusive

    def __repr__(self) -> str:
        base = super().__repr__()
        return f"{base[:-1]}, exclusive={self.exclusive!r})"


def main() -> None:
    csv_movie = Movie.from_csv("Inception,2010,Christopher Nolan,Science fiction,8.8")
    dictionary_movie = Movie.from_dict(
        {
            "title": "The Matrix",
            "year": 1999,
            "director": "The Wachowskis",
            "genre": "Science fiction",
            "rating": 8.7,
        }
    )
    premium_csv = PremiumMovie.from_csv("Dune,2021,Denis Villeneuve,Science fiction,8.0")
    premium_dictionary = PremiumMovie.from_dict(
        {
            "title": "Arrival",
            "year": 2016,
            "director": "Denis Villeneuve",
            "genre": "Science fiction",
            "rating": 7.9,
        }
    )
    print(f"CSV factory: {csv_movie!r}")
    print(f"Dictionary factory: {dictionary_movie!r}")
    print(f"Premium CSV type: {type(premium_csv).__name__} · {premium_csv!r}")
    print(f"Premium dictionary type: {type(premium_dictionary).__name__} · {premium_dictionary!r}")
    print(f"Class validation: {Movie.validate_rating(8.5)}")
    print(f"Instance validation: {csv_movie.validate_rating(15.0)}")


if __name__ == "__main__":
    main()
