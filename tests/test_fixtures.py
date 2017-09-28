import pytest
from sea.tests.fixtures import *
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator.database_manager import DatabaseManager


def test_app(app):
    assert app is not None


def test_migrate(migrator):
    assert isinstance(migrator._repository, DatabaseMigrationRepository)
    assert isinstance(migrator._connection, DatabaseManager)
    assert migrator._connection is not None
