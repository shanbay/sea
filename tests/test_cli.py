import sys
import pytest
import os
import shutil
from unittest import mock

from sea import cli, current_app


def test_abscmd():
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.opt(mock.Mock(), mock.Mock())
    with pytest.raises(NotImplementedError):
        cli.AbstractCommand.run(mock.Mock(), mock.Mock())


def test_cmd_server(app):
    sys.argv = 'sea s -b 127.0.0.1'.split()
    with mock.patch('sea.cli.Server', autospec=True) as mocked:
        assert cli.main() == 0
        mocked.return_value.run.assert_called_with()


def test_cmd_console(app):
    sys.argv = 'sea c'.split()
    mocked = mock.MagicMock()
    with mock.patch.dict('sys.modules', {'IPython': mocked}):
        assert cli.main() == 0
        assert mocked.embed.called


def test_generate(app):
    sys.argv = 'sea g -I /path/to/protos hello.proto test.proto'.split()
    with mock.patch('grpc_tools.protoc.main', return_value=0) as mocked:
        assert cli.main() == 0
        proto_out = os.path.join(app.root_path, 'protos')
        cmd = [
            'grpc_tools.protoc',
            '--proto_path', '/path/to/protos',
            '--python_out', proto_out,
            '--grpc_python_out', proto_out,
            '/path/to/protos/hello.proto',
            '/path/to/protos/test.proto'
        ]
        mocked.assert_called_with(cmd)


def test_cmd_new():
    shutil.rmtree('tests/myproject', ignore_errors=True)
    sys.argv = ('sea new tests/myproject'
                ' --skip-git --skip-consul --skip-orator').split()
    assert cli.main() == 0
    correct_code = """\
    # import myproject_pb2
    # import myproject_pb2_grpc

    # from sea.servicer import ServicerMeta


    # class MyprojectServicer(myproject_pb2_grpc.MyprojectServicer, metaclass=ServicerMeta):

    #     pass
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
    raven
    """
    with open('./tests/myproject/requirements.txt', 'r') as f:
        content = f.read()
    assert content == dedent(correct_code)

    shutil.rmtree('tests/myproject')


def test_cmd_job(app):
    sys.argv = 'seak plusone -n 100'.split()
    assert cli.jobmain() == 0
    assert current_app.config.get('NUMBER') == 101
    sys.argv = 'seak config_hello'.split()
    assert isinstance(cli.jobmain(), cli.JobException)

    class EntryPoint:
        def load(self):
            @cli.jobm.job('xyz')
            def f2():
                current_app.config['XYZ'] = 'hello'
            return f2

    def new_entry_iter(name):
        return [EntryPoint()]

    with mock.patch('pkg_resources.iter_entry_points', new=new_entry_iter):
        sys.argv = 'seak xyz'.split()
        assert cli.jobmain() == 0
        assert current_app.config.get('XYZ') == 'hello'


def test_main():
    sys.argv = 'sea -h'.split()
    with pytest.raises(SystemExit):
        cli.main()
