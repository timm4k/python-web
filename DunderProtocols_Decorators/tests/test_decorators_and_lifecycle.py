import pytest

from cinema_protocols.context_demo import MovieCache, MovieSession
from cinema_protocols.decorators_demo import create_unstable_api_call, retry, timed
from cinema_protocols.movies import create_sample_movies


def test_timed_preserves_metadata_and_reports_duration(capsys: pytest.CaptureFixture[str]) -> None:
    @timed
    def calculate() -> int:
        """Return a result"""
        return 42

    assert calculate() == 42
    assert calculate.__name__ == "calculate"
    assert calculate.__doc__ == "Return a result"
    assert "[timed] calculate" in capsys.readouterr().out


def test_retry_succeeds_after_failures() -> None:
    events: list[str] = []
    call = create_unstable_api_call(2, max_attempts=3, delay=0, reporter=events.append)
    assert call("https://example.test") == "200 OK: https://example.test"
    assert len(events) == 2
    assert call.__name__ == "unstable_api_call"


def test_retry_exhaustion_preserves_cause() -> None:
    call = create_unstable_api_call(3, max_attempts=2, delay=0, reporter=lambda _: None)
    with pytest.raises(RuntimeError, match="after 2 attempts") as captured:
        call("https://example.test")
    assert isinstance(captured.value.__cause__, ConnectionError)


def test_retry_configuration_validation() -> None:
    with pytest.raises(ValueError):
        retry(max_attempts=0)
    with pytest.raises(TypeError):
        retry(max_attempts=True)
    with pytest.raises(ValueError):
        retry(delay=-1)


def test_singleton_decorator_returns_same_cache() -> None:
    first = MovieCache()
    second = MovieCache()
    first.clear()
    first.add(create_sample_movies()[0])
    assert first is second
    assert len(second) == 1


def test_context_manager_reports_full_lifecycle() -> None:
    events: list[str] = []
    movie = create_sample_movies()[0]
    with MovieSession("Evening", reporter=events.append) as session:
        session.add(movie)
    assert "started" in events[0]
    assert str(movie) in events[1]
    assert "finished" in events[2]


def test_context_manager_reports_and_propagates_error() -> None:
    events: list[str] = []
    with pytest.raises(RuntimeError, match="projection failed"):
        with MovieSession("Evening", reporter=events.append):
            raise RuntimeError("projection failed")
    assert any("Error: projection failed" in event for event in events)
    assert "finished" in events[-1]
