import os
import pytest

import sea
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator.database_manager import DatabaseManager

os.environ.setdefault('SEA_ENV', 'testing')


@pytest.fixture(scope='module')
def testing_migrate():
    app = sea.create_app(os.getcwd())
    database = 'sqlite'
    resolver = DatabaseManager(app.config.get('ORATOR').DATABASES)
    repository = DatabaseMigrationRepository(resolver, 'migrations')
    migrator = Migrator(repository, resolver)

    migrator.set_connection(database)

    if not migrator.repository_exists():
        repository.set_source(database)
        repository.create_repository()
    path = 'db/migrations'

    migrator.run(path, False)
    yield app
    os.remove('/tmp/orator_test.db')
    sea._app = None
