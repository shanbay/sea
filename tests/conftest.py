import pytest
import logging
import os
from io import StringIO

import sea
from sea.test.fixtures import *  # noqa


@pytest.fixture
def logstream():
    return StringIO()


@pytest.fixture
def app(logstream):
    os.environ.setdefault("SEA_ENV", "testing")
    logger = logging.getLogger("sea")
    h = logging.StreamHandler(logstream)
    logger.addHandler(h)
    root = os.path.join(os.path.dirname(__file__), "wd")
    app = sea.create_app(root)
    yield app
    logger.removeHandler(h)
    sea._app = None
