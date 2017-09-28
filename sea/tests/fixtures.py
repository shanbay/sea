import os
import pytest

import sea
from sea.contrib.extensions.orator import Orator
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator.database_manager import DatabaseManager

os.environ.setdefault('SEA_ENV', 'testing')


@pytest.fixture(scope='module')
def app():
    app = sea.create_app(
        os.path.join(
            os.path.dirname(__file__), 'wd'))
    yield app
    sea._app = None


@pytest.fixture(scope='module')
def migrator():
    app = sea.create_app(
        os.path.join(
            os.path.dirname(__file__), 'wd'))
    config = app.config.get('ORATOR').DATABASES
    default_connection = config[config['default']]
    database = default_connection['driver']
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
    sea._app = None
