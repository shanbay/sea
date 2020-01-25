import pytest

from sea import current_app


@pytest.fixture
def app():
    return current_app
