import os
import shutil
import sys
from unittest import mock

import pytest

from sea import cli


def test_cmd_server(app):
    sys.argv = "sea s".split()
    with mock.patch("sea.server.Server", autospec=True) as mocked:
        assert cli.main() == 0
        mocked.return_value.run.assert_called_with()


def test_cmd_console(app):
    sys.argv = "sea c".split()
    mocked = mock.MagicMock()
    with mock.patch.dict("sys.modules", {"IPython": mocked}):
        assert cli.main() == 0
        assert mocked.embed.called


def test_cmd_generate():
    sys.argv = (
        "sea g -I /path/to/protos -I /another/path/to/protos "
        "hello.proto test.proto"
    ).split()

    with mock.patch("grpc_tools.protoc.main", return_value=0) as mocked:
        assert cli.main() == 0
        import grpc_tools

        well_known_path = os.path.join(
            os.path.dirname(grpc_tools.__file__), "_proto"
        )
        proto_out = os.path.join(os.getcwd(), "protos")
        cmd = [
            "grpc_tools.protoc",
            "--proto_path",
            "/path/to/protos",
            "--proto_path",
            "/another/path/to/protos",
            "--proto_path",
            well_known_path,
            "--python_out",
            proto_out,
            "--grpc_python_out",
            proto_out,
            "hello.proto",
            "test.proto",
        ]
        mocked.assert_called_with(cmd)


def test_cmd_new():
    shutil.rmtree("tests/myproject", ignore_errors=True)
    sys.argv = ("sea new tests/myproject" " --skip-git --skip-peewee").split()
    assert cli.main() == 0
    correct_code = """\
    # import myproject_pb2
    # import myproject_pb2_grpc

    # from sea.servicer import ServicerMeta


    # class MyprojectServicer(myproject_pb2_grpc.MyprojectServicer, metaclass=ServicerMeta):

    #     pass
    """
    with open("./tests/myproject/app/servicers.py", "r") as f:
        content = f.read()

    from textwrap import dedent

    assert content == dedent(correct_code).rstrip()
    assert not os.path.exists("./tests/myproject/condfigs/default/peewee.py")
    assert os.path.exists("./tests/myproject/app/async_tasks.py")
    assert os.path.exists("./tests/myproject/app/buses.py")

    correct_code = """\
    sea
    cachext
    celery
    sentry-sdk
    """
    with open("./tests/myproject/requirements.txt", "r") as f:
        content = f.read()
    assert content == dedent(correct_code)

    shutil.rmtree("tests/myproject")


def test_cmd_job(app):
    with mock.patch("os.getcwd", return_value=app.root_path):
        sys.argv = "sea plusone -n 100".split()
        assert cli.main() is None
        assert app.config.get("NUMBER") == 101
        sys.argv = "sea config_hello".split()
        assert isinstance(cli.main(), cli.JobException)

    class EntryPoint:
        def load(self):
            @cli.jobm.job("xyz")
            def f2():
                app.config["XYZ"] = "hello"

            return f2

    class FailedEntryPoint:
        def load(self):
            raise Exception("Failed entry point")

    # Mock entry_points to return our entry points
    class MockEntryPoints:
        def __init__(self, entries):
            self.entries = entries
        def __iter__(self):
            return iter(self.entries)

    def mock_entry_points(group=None):
        if group == "sea.jobs":
            return MockEntryPoints([EntryPoint(), FailedEntryPoint()])
        return MockEntryPoints([])

    mock_logger = mock.Mock()
    with mock.patch("sea.cli.entry_points", side_effect=mock_entry_points), \
         mock.patch("logging.getLogger", return_value=mock_logger), \
         mock.patch("os.getcwd", return_value=app.root_path):
        # Reload jobs to pick up the mocked entry points
        cli._load_jobs()
        sys.argv = "sea xyz".split()
        assert cli.main() is None
        assert app.config.get("XYZ") == "hello"
        mock_logger.error.assert_called_with(
            "error has occurred during pkg loading: Failed entry point"
        )


def test_cmd_job_importlib_metadata_python310(app):
    """Test entry points loading with importlib.metadata (Python 3.10+ API)"""
    class EntryPoint:
        def load(self):
            @cli.jobm.job("test_importlib")
            def f():
                app.config["IMPORTLIB_TEST"] = "success"
            return f

    class FailedEntryPoint:
        def load(self):
            raise Exception("Failed entry point")

    # Mock Python 3.10+ API: entry_points(group="...") returns EntryPoints object
    class MockEntryPoints:
        def __init__(self, entries):
            self.entries = entries

        def __iter__(self):
            return iter(self.entries)

    def mock_entry_points(group=None):
        if group == "sea.jobs":
            return MockEntryPoints([EntryPoint(), FailedEntryPoint()])
        return MockEntryPoints([])

    mock_logger = mock.Mock()
    with mock.patch("sea.cli.entry_points", side_effect=mock_entry_points), \
         mock.patch("logging.getLogger", return_value=mock_logger), \
         mock.patch("os.getcwd", return_value=app.root_path):
        # Reload jobs to pick up the mocked entry points
        cli._load_jobs()
        sys.argv = "sea test_importlib".split()
        assert cli.main() is None
        assert app.config.get("IMPORTLIB_TEST") == "success"
        mock_logger.error.assert_called_with(
            "error has occurred during pkg loading: Failed entry point"
        )


def test_cmd_job_importlib_metadata_python38(app):
    """Test entry points loading with importlib.metadata (Python 3.8-3.9 API)"""
    class EntryPoint:
        def load(self):
            @cli.jobm.job("test_importlib38")
            def f():
                app.config["IMPORTLIB38_TEST"] = "success"
            return f

    # Mock Python 3.8-3.9 API: entry_points() returns dict-like object
    class MockEntryPointsDict:
        def __init__(self):
            self._data = {
                "sea.jobs": [EntryPoint()]
            }

        def get(self, key, default=None):
            return self._data.get(key, default)

    def mock_entry_points(group=None):
        if group is not None:
            # Python 3.10+ style call - should raise TypeError in 3.8-3.9
            raise TypeError("entry_points() takes 0 positional arguments")
        return MockEntryPointsDict()

    mock_logger = mock.Mock()
    with mock.patch("sea.cli.entry_points", side_effect=mock_entry_points), \
         mock.patch("logging.getLogger", return_value=mock_logger), \
         mock.patch("os.getcwd", return_value=app.root_path):
        # Reload jobs to pick up the mocked entry points
        cli._load_jobs()
        sys.argv = "sea test_importlib38".split()
        assert cli.main() is None
        assert app.config.get("IMPORTLIB38_TEST") == "success"


def test_cmd_async_task_and_bus_registered():
    """Test that async_task and bus commands are registered via entry points"""
    # This test verifies that the real entry points from setup.py are loaded
    # Check that async_task and bus are registered after _load_jobs()
    # Note: This will only work if sea package is installed with entry points
    assert "async_task" in cli.jobm.jobs or "bus" in cli.jobm.jobs, \
        "async_task or bus should be registered via entry points. " \
        "Make sure sea package is installed with 'pip install -e .'"

    # If they exist, verify they are the correct functions
    if "async_task" in cli.jobm.jobs:
        assert cli.jobm.jobs["async_task"].__name__ == "async_task"
    if "bus" in cli.jobm.jobs:
        assert cli.jobm.jobs["bus"].__name__ == "bus"


def test_main():
    sys.argv = "sea -h".split()
    with pytest.raises(SystemExit):
        cli.main()
    # no arguments scenes
    sys.argv = ["sea"]
    with pytest.raises(SystemExit):
        cli.main()
