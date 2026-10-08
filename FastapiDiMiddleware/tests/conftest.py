from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


@pytest.fixture
def client() -> Iterator[TestClient]:
    application = create_app(Settings(rate_limit=200))
    with TestClient(application, base_url="http://localhost") as test_client:
        yield test_client
