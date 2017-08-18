from unittest import mock

from sea.contrib.extensions import orator


def test_orator(app):
    c = orator.Orator()
    assert c._dbmanager is None
    c.init_app(app)
    assert isinstance(c._dbmanager, orator.orator.DatabaseManager)
    with mock.patch.object(c._dbmanager, 'connection') as mocked:
        c.connection()
        mocked.assert_called_once_with()


def test_model_meta(cache, table_user):
    from app.models import User

    assert hasattr(User, 'find_by')

    jack = User.create(username='jack', age=35)
    key = User.find_by.make_cache_key(User, 'username', 'jack')
    assert not cache.exists(key)
    assert User.find_by('username', 'jack').id == jack.id
    assert cache.exists(key)

    jane = User.create(username='jane', age=31)
    assert User.find(jane.id).username == jane.username
    key = User.find.make_cache_key(User, jane.id)
    assert cache.exists(key)
    jane.husband().associate(jack)
    jane.save()
    assert not cache.exists(key)

    c1 = User.create(username='c1', age=5)
    c2 = User.create(username='c2', age=2)
    User.find(c1.id)
    children = User.find([c1.id, c2.id])
    key = User.find.make_cache_key(User, c2.id)
    assert cache.exists(key)
    assert len(children) == 2
    jack.children().save_many([c1, c2])
    assert not cache.exists(key)
