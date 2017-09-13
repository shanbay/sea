from unittest import mock
import sys
import pytest

from sea.contrib.extensions import orator
from sea.contrib.extensions.orator import cli


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
    with mock.patch('sea.contrib.extensions.orator.cache_model._bulk_register_to_related_caches') as mocked:
        User.find([c1.id, c2.id])
        assert not mocked.called
    jack.children().save_many([c1, c2])
    assert not cache.exists(key)


def test_cli(app):
    sys.argv = ['seaorator', '-h']
    with pytest.raises(SystemExit):
        cli.main()

    with mock.patch('sea.contrib.extensions.orator.cli.application'):
        with mock.patch.object(app, 'root_path', new='.'):
            sys.argv = 'seaorator help'.split()
            cli.main()
            assert sys.argv == 'orator help'.split()

            sys.argv = 'seaorator list'.split()
            cli.main()
            assert sys.argv == 'orator list'.split()

            sys.argv = 'seaorator migrate'.split()
            cli.main()
            assert sys.argv[1] == 'migrate'
            argv = ' '.join(sys.argv)
            assert '--config ./configs/default/orator.py' in argv
            assert '--path ./db/migrations' in argv

            sys.argv = 'seaorator db:seed'.split()
            cli.main()
            assert sys.argv[1] == 'db:seed'
            argv = ' '.join(sys.argv)
            assert '--config ./configs/default/orator.py' in argv
            assert '--path ./db/seeds' in argv

            sys.argv = 'seaorator make:migration'.split()
            cli.main()
            assert sys.argv[1] == 'make:migration'
            argv = ' '.join(sys.argv)
            assert '--path ./db/migrations' in argv

            sys.argv = 'seaorator make:seed'.split()
            cli.main()
            assert sys.argv[1] == 'make:seed'
            argv = ' '.join(sys.argv)
            assert '--path ./db/seeds' in argv

            sys.argv = 'seaorator migrate:reset'.split()
            cli.main()
            assert sys.argv[1] == 'migrate:reset'
            argv = ' '.join(sys.argv)
            assert '--config ./configs/default/orator.py' in argv
            assert '--path ./db/migrations' in argv

            sys.argv = 'seaorator migrate:rollback'.split()
            cli.main()
            assert sys.argv[1] == 'migrate:rollback'
            argv = ' '.join(sys.argv)
            assert '--config ./configs/default/orator.py' in argv
            assert '--path ./db/migrations' in argv

            sys.argv = 'seaorator migrate:status'.split()
            cli.main()
            assert sys.argv[1] == 'migrate:status'
            argv = ' '.join(sys.argv)
            assert '--config ./configs/default/orator.py' in argv
            assert '--path ./db/migrations' in argv
