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
    sys.argv = 'sea s -b 127.0.0.1 -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = 'sea -w ./tests/wd s -b 127.0.0.1'.split()
    with mock.patch('sea.cli.Server', autospec=True):
        assert isinstance(cli.main(), mock.Mock)


def test_cmd_console():
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
    sys.argv = 'sea new -f wrong'.split()
    with pytest.raises(ValueError):
        cli.main()
    sys.argv = ('sea new myproject'
                ' --skip-git --skip-consul --skip-orator').split()
    cli.main()
    correct_code = """\
    import myproject_pb2
    import myproject_pb2_grpc

    from sea.servicer import ServicerMeta


    class GreeterServicer(myproject_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):

        DEFAULT_MSG_CLASS = myproject_pb2.EmptyReply
    """
    with open('./myproject/app/servicers.py', 'r') as f:
        content = f.read()
    import os, shutil
    from textwrap import dedent
    assert content == dedent(correct_code).rstrip()
    assert not os.path.exists('./myproject/condfigs/development/orator.py')
    shutil.rmtree('myproject')


def test_cmd_task():
    sys.argv = 'sea -w ./tests/wd i plusone -n 100'.split()
    assert cli.main() == 101
    sys.argv = 'sea -w ./tests/wd i getconfig'.split()
    assert cli.main()

    class EntryPoint:
        def load(self):
            @cli.taskm.task('xyz')
            def f2():
                return "hello"
            return f2

    def new_entry_iter(name):
        return [EntryPoint()]

    with mock.patch('pkg_resources.iter_entry_points', new=new_entry_iter):
        sys.argv = 'sea -w ./tests/wd i xyz'.split()
        assert cli.main() == 'hello'
