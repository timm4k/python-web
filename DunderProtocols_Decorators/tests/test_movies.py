from typing import Any, cast

import pytest

from cinema_protocols.movie_factories import PremiumMovie
from cinema_protocols.movies import Movie


@pytest.fixture
def movie() -> Movie:
    return Movie("Inception", 2010, "Christopher Nolan", "Science fiction", 8.8)


def test_representation_protocols(movie: Movie) -> None:
    assert str(movie) == "Inception (2010) — 8.8 ★"
    assert repr(movie) == (
        "Movie(title='Inception', year=2010, director='Christopher Nolan', "
        "genre='Science fiction', rating=8.8)"
    )


def test_equality_and_hash_use_title_and_year(movie: Movie) -> None:
    duplicate = Movie("Inception", 2010, "Another", "Drama", 1.0)
    assert movie == duplicate
    assert hash(movie) == hash(duplicate)
    assert len({movie, duplicate}) == 1
    assert {movie: "stored"}[duplicate] == "stored"


def test_total_ordering_compares_ratings(movie: Movie) -> None:
    higher = Movie("The Dark Knight", 2008, "Christopher Nolan", "Crime", 9.0)
    assert movie < higher
    assert higher > movie
    assert movie <= higher
    assert higher >= movie


def test_unknown_comparison_returns_not_implemented(movie: Movie) -> None:
    assert movie.__eq__("Inception") is NotImplemented
    assert movie.__lt__(8.8) is NotImplemented


@pytest.mark.parametrize("rating", [-0.1, 10.1, True, "8.8"])
def test_invalid_rating_is_rejected(rating: object) -> None:
    assert Movie.validate_rating(rating) is False
    with pytest.raises(ValueError, match="Rating"):
        Movie("Title", 2020, "Director", "Genre", cast(Any, rating))


def test_factories_create_movie() -> None:
    csv_movie = Movie.from_csv("Arrival,2016,Denis Villeneuve,Science fiction,7.9")
    dict_movie = Movie.from_dict(
        {
            "title": "Arrival",
            "year": 2016,
            "director": "Denis Villeneuve",
            "genre": "Science fiction",
            "rating": 7.9,
        }
    )
    assert csv_movie == dict_movie


def test_inherited_factory_preserves_runtime_type() -> None:
    movie = PremiumMovie.from_csv("Dune,2021,Denis Villeneuve,Science fiction,8.0")
    assert isinstance(movie, PremiumMovie)
    assert movie.exclusive is True
    assert "exclusive=True" in repr(movie)


def test_invalid_factory_data_is_rejected() -> None:
    with pytest.raises(ValueError, match="CSV must contain"):
        Movie.from_csv("Incomplete,2020")
    with pytest.raises(ValueError, match="Missing movie fields"):
        Movie.from_dict({"title": "Incomplete"})
    with pytest.raises(ValueError, match="must be strings"):
        Movie.from_dict(
            {
                "title": None,
                "year": 2020,
                "director": "Director",
                "genre": "Genre",
                "rating": 8.0,
            }
        )
    with pytest.raises(ValueError, match="Year must be an integer"):
        Movie.from_dict(
            {
                "title": "Title",
                "year": "2020",
                "director": "Director",
                "genre": "Genre",
                "rating": 8.0,
            }
        )
