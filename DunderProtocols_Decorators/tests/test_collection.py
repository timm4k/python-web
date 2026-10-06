import pytest

from cinema_protocols.movie_collection import MovieCollection
from cinema_protocols.movies import Movie, create_sample_movies


@pytest.fixture
def collection() -> MovieCollection:
    return MovieCollection(list(create_sample_movies()[:3]))


def test_container_protocol(collection: MovieCollection) -> None:
    first = create_sample_movies()[0]
    assert len(collection) == 3
    assert bool(collection) is True
    assert collection[0] == first
    assert first in collection
    assert "inception" in collection
    assert list(collection)[0] == first


def test_index_protocol_keeps_list_error(collection: MovieCollection) -> None:
    with pytest.raises(IndexError):
        _ = collection[99]


def test_add_returns_new_unique_collection(collection: MovieCollection) -> None:
    movies = create_sample_movies()
    other = MovieCollection(list(movies[2:]))
    combined = collection + other
    assert isinstance(combined, MovieCollection)
    assert len(combined) == 5
    assert len(collection) == 3


def test_add_unknown_type_returns_not_implemented(collection: MovieCollection) -> None:
    assert collection.__add__([create_sample_movies()[0]]) is NotImplemented


def test_add_and_remove(collection: MovieCollection) -> None:
    movie = Movie("Arrival", 2016, "Denis Villeneuve", "Science fiction", 7.9)
    collection.add(movie)
    collection.add(movie)
    assert len(collection) == 4
    assert collection.remove("arrival") is True
    assert collection.remove("missing") is False


def test_top_rated_and_validation(collection: MovieCollection) -> None:
    assert [movie.rating for movie in collection.top_rated(2)] == [9.0, 8.8]
    with pytest.raises(ValueError, match="non-negative"):
        collection.top_rated(-1)
