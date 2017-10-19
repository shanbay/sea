import os
import pytest


@pytest.fixture
def db(app):
    from orator.migrations import Migrator, DatabaseMigrationRepository
    db = app.extensions.db
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
    cache = app.extensions.cache
    cache.clear()
    yield cache
    cache.clear()
