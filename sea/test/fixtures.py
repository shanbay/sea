import os
import pytest
import logging
from io import StringIO

import sea
from orator.migrations import Migrator, DatabaseMigrationRepository


@pytest.fixture(scope='session')
def logstream():
    return StringIO()


@pytest.fixture(scope='module')
def app(logstream):
    os.environ.setdefault('SEA_ENV', 'testing')
    logger = logging.getLogger('sea')
    h = logging.StreamHandler(logstream)
    logger.addHandler(h)
    root = os.getcwd()
    if 'app' in os.listdir(root):
        app = sea.create_app(root)
    else:
        app = sea.create_app(os.path.join(root, 'tests/wd'))
    yield app
    logger.removeHandler(h)
    logstream.truncate(0)
    logstream.seek(0)
    sea._app = None


@pytest.fixture(scope='module')
def db(app):
    db = app.extensions['db']
    repository = DatabaseMigrationRepository(db, 'migrations')
    migrator = Migrator(repository, db)

    if not migrator.repository_exists():
        repository.create_repository()
    path = os.path.join(app.root_path, 'db/migrations')

    migrator.run(path)
    yield db
    migrator.rollback(path)


@pytest.fixture
def cache(app):
    cache = app.extensions['cache']
    cache.clear()
    yield cache
    cache.clear()