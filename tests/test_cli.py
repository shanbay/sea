import os
import sys
import pytest
from unittest import mock

from sea import cli


def test_abscmd():
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.opt(mock.Mock(), mock.Mock())
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.run(mock.Mock(), mock.Mock())


def test_cmd_server():
    os.environ.setdefault('SEA_ENV', 'testing')
    sys.argv = 'sea s -b 127.0.0.1 -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea -w ./tests/wd s -b 127.0.0.1'.split()
    with mock.patch('sea.cli.Server', autospec=True):
        assert isinstance(cli.main(), mock.Mock)


def test_cmd_console():
    os.environ.setdefault('SEA_ENV', 'testing')
    sys.argv = 'sea c -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea -w ./tests/wd c'.split()
    mocked = mock.MagicMock()
    mocked.embed = mock.MagicMock(return_value='Embed Called')
    mocked.interact = mock.MagicMock(return_value='Interact Called')
    with mock.patch.dict('sys.modules', {'IPython': mocked}):
        assert cli.main() == 'Embed Called'
        mocked.embed.side_effect = ImportError
        with mock.patch('sea.cli.code', new=mocked):
            assert cli.main() == 'Interact Called'


def test_cmd_new():
    os.environ.setdefault('SEA_ENV', 'testing')
    sys.argv = 'sea new -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea new myproject'.split()
    # TODO


def test_cmd_task():
    os.environ.setdefault('SEA_ENV', 'testing')
    sys.argv = 'sea -w ./tests/wd i plusone -n 100'.split()
    assert cli.main() == 101
