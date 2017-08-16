import sys
import pytest
import os
import shutil
from unittest import mock

from sea import cli


def test_abscmd():
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.opt(mock.Mock(), mock.Mock())
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.run(mock.Mock(), mock.Mock())


def test_cmd_server():
    sys.argv = 'sea s -b 127.0.0.1 -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea -w ./tests/wd s -b 127.0.0.1'.split()
    with mock.patch('sea.cli.Server', autospec=True) as mocked:
        cli.main()
        mocked.return_value.run.assert_called_with()


def test_cmd_console():
    sys.argv = 'sea c -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea -w ./tests/wd c'.split()
    mocked = mock.MagicMock()
    with mock.patch.dict('sys.modules', {'IPython': mocked, 'code': mocked}):
        cli.main()
        assert mocked.embed.called
        mocked.embed.side_effect = ImportError
        cli.main()
        assert mocked.interact.called


def test_cmd_new():
    shutil.rmtree('tests/myproject', ignore_errors=True)
    sys.argv = 'sea new -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = ('sea new tests/myproject'
                ' --skip-git --skip-consul --skip-orator').split()
    cli.main()
    correct_code = """\
    import myproject_pb2
    import myproject_pb2_grpc

    from sea.servicer import ServicerMeta


    class MyprojectServicer(myproject_pb2_grpc.MyprojectServicer, metaclass=ServicerMeta):

        pass
    """
    with open('./tests/myproject/app/servicers.py', 'r') as f:
        content = f.read()

    from textwrap import dedent
    assert content == dedent(correct_code).rstrip()
    assert not os.path.exists('./tests/myproject/condfigs/development/orator.py')
    assert os.path.exists('./tests/myproject/app/tasks.py')

    correct_code = """\
    redis
    celery
    pytest
    """
    with open('./tests/myproject/requirements.txt', 'r') as f:
        content = f.read()
    assert content == dedent(correct_code).rstrip()

    shutil.rmtree('tests/myproject')


def test_cmd_job():
    sys.argv = 'sea -w ./tests/wd i plusone -n 100'.split()
    assert cli.main() == 101
    sys.argv = 'sea -w ./tests/wd i getconfig'.split()
    assert cli.main()

    class EntryPoint:
        def load(self):
            @cli.jobm.job('xyz')
            def f2():
                return "hello"
            return f2

    def new_entry_iter(name):
        return [EntryPoint()]

    with mock.patch('pkg_resources.iter_entry_points', new=new_entry_iter):
        sys.argv = 'sea -w ./tests/wd i xyz'.split()
        assert cli.main() == 'hello'
