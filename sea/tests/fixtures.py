import os
import pytest

import sea
from sea.contrib.extensions.orator import Orator
from sea.contrib.extensions.cache import Cache
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator.database_manager import DatabaseManager

os.environ.setdefault('SEA_ENV', 'testing')


@pytest.fixture(scope='module')
def app():
    app = sea.create_app(os.getcwd())
    yield app
    sea._app = None


@pytest.fixture(scope='module')
def migrator(app):
    config = app.config.get('DATABASES')
    database = config['default']
    resolver = DatabaseManager(config)
    repository = DatabaseMigrationRepository(resolver, 'migrations')
    migrator = Migrator(repository, resolver)

    migrator.set_connection(database)

    if not migrator.repository_exists():
        repository.set_source(database)
        repository.create_repository()
    path = 'db/migrations'

    migrator.run(path, False)
    yield migrator
    migrator.rollback(path, False)


@pytest.fixture(scope='module')
def db(app):
    db = Orator()
    app.register_extension('db', db)
    yield db
    app.extensions.pop('db')


@pytest.fixture
def cache(app):
    cache = Cache()
    app.register_extension('cache', cache)
    cache.clear()
    yield cache
    cache.clear()
    app.extensions.pop('cache')
