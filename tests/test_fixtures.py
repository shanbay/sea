import os
import pytest
import sys
import sea
from sea.tests.fixtures import migrator
from orator.migrations import Migrator, DatabaseMigrationRepository
from orator.database_manager import DatabaseManager


# def test_app(app):
#     assert app is not None


def test_migrate(app):
    assert app is not None

    mig = next(migrator(app))
    assert isinstance(mig._repository, DatabaseMigrationRepository)
    assert isinstance(mig._resolver, DatabaseManager)
    assert mig._connection is not None
    assert mig.repository_exists()
