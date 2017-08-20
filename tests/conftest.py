import os
import pytest
from orator import Schema

import sea
from sea.contrib.extensions.orator import Orator
from sea.contrib.extensions.cache import Cache

os.environ.setdefault('SEA_ENV', 'testing')


@pytest.fixture(scope='module')
def app():
    app = sea.create_app(
        os.path.join(
            os.path.dirname(__file__), 'wd'))
    yield app
    sea._app = None


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


@pytest.fixture
def table_user(db):
    schema = Schema(db)
    with schema.create('users') as table:
        table.big_increments('id')
        table.string('username')
        table.integer('age').unsigned().default(1)
        table.timestamps()
        table.big_integer('husband_id').nullable()
        table.big_integer('father_id').nullable()
    yield db.table('users')
    schema.drop('users')
