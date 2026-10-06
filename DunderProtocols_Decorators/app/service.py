import time

from cinema_protocols.context_demo import MovieCache, MovieSession
from cinema_protocols.decorators_demo import create_unstable_api_call
from cinema_protocols.movie_collection import MovieCollection
from cinema_protocols.movie_factories import PremiumMovie
from cinema_protocols.movies import Movie, create_sample_movies

from .catalog import PROTOCOL_GUIDES
from .schemas import CollectionRequest, FactoryRequest, RetryRequest, SessionRequest

MOVIES = create_sample_movies()
DEMO_API_URL = "https://cinema.example/movies"
SESSION_NAME = "Protocol screening"
CollectionResult = bool | int | str | list[str]

COLLECTION_METHODS = {
    "length": "__len__",
    "truth": "__bool__",
    "index": "__getitem__",
    "contains": "__contains__",
    "iterate": "__iter__",
    "merge": "__add__",
    "top": "top_rated",
}


def overview() -> dict[str, object]:
    return {
        "guides": [
            {
                "label": guide.label,
                "file": guide.file_name,
                "methods": guide.methods,
                "meaning": guide.meaning,
                "outcome": guide.outcome,
            }
            for guide in PROTOCOL_GUIDES
        ]
    }


def movie_protocols() -> dict[str, object]:
    sorted_movies = sorted(MOVIES, reverse=True)
    duplicate = Movie.from_dict(
        {
            "title": MOVIES[0].title,
            "year": MOVIES[0].year,
            "director": "Another director",
            "genre": "Another genre",
            "rating": 1.0,
        }
    )
    unique_movies = {*MOVIES, duplicate}
    movie_ratings = {movie: movie.rating for movie in MOVIES}
    return {
        "selected": {"repr": repr(MOVIES[0]), "str": str(MOVIES[0])},
        "sorted": [str(movie) for movie in sorted_movies],
        "setCount": len(unique_movies),
        "sourceCount": len(MOVIES) + 1,
        "dictionaryLookup": movie_ratings[MOVIES[0]],
        "identityRule": "title + year",
    }


def run_collection(request: CollectionRequest) -> dict[str, object]:
    first = MovieCollection(list(MOVIES[:3]))
    second = MovieCollection(list(MOVIES[2:]))
    operation = request.operation
    if operation == "length":
        result: CollectionResult = len(first)
        expression = "len(collection)"
    elif operation == "truth":
        result = bool(first)
        expression = "bool(collection)"
    elif operation == "index":
        result = str(first[request.index])
        expression = f"collection[{request.index}]"
    elif operation == "contains":
        result = request.title in first
        expression = f"{request.title!r} in collection"
    elif operation == "iterate":
        result = [str(movie) for movie in first]
        expression = "for movie in collection"
    elif operation == "merge":
        result = [str(movie) for movie in first + second]
        expression = "first + second"
    else:
        result = [str(movie) for movie in first.top_rated(request.count)]
        expression = f"collection.top_rated({request.count})"
    return {
        "expression": expression,
        "method": COLLECTION_METHODS[operation],
        "result": result,
    }


def run_factory(request: FactoryRequest) -> dict[str, object]:
    movie_type = PremiumMovie if request.premium else Movie
    if request.source == "csv":
        movie = movie_type.from_csv(request.csv_line)
    else:
        source_data = {
            "title": request.title,
            "year": request.year,
            "director": request.director,
            "genre": request.genre,
            "rating": request.rating,
        }
        movie = movie_type.from_dict(source_data)
    return {
        "constructor": f"{movie_type.__name__}.from_{request.source}",
        "type": type(movie).__name__,
        "display": str(movie),
        "repr": repr(movie),
    }


def run_retry(request: RetryRequest) -> dict[str, object]:
    events: list[str] = []
    api_call = create_unstable_api_call(
        failures_before_success=request.failures_before_success,
        max_attempts=request.max_attempts,
        delay=0,
        reporter=events.append,
    )
    started_at = time.perf_counter()
    try:
        result = api_call(DEMO_API_URL)
        status = "completed"
    except RuntimeError as error:
        result = str(error)
        status = "exhausted"
    return {
        "status": status,
        "events": events,
        "result": result,
        "elapsedMilliseconds": round((time.perf_counter() - started_at) * 1000, 3),
        "functionName": api_call.__name__,
        "documentation": api_call.__doc__,
    }


def run_session(request: SessionRequest) -> dict[str, object]:
    if any(index < 0 or index >= len(MOVIES) for index in request.movie_indexes):
        raise ValueError("Every movie index must identify a catalog movie")
    events: list[str] = []
    cache_one = MovieCache()
    cache_two = MovieCache()
    cache_one.clear()
    with MovieSession(SESSION_NAME, reporter=events.append) as session:
        for index in request.movie_indexes:
            movie = MOVIES[index]
            session.add(movie)
            cache_one.add(movie)
        summary = str(session)
    return {
        "events": events,
        "summary": summary,
        "sameCache": cache_one is cache_two,
        "cachedCount": len(cache_two),
    }
