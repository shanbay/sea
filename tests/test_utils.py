import pytest
from sea import utils


def test_import_string():
    from sea.app import Sea
    import datetime
    assert utils.import_string('datetime.date') is datetime.date
    assert utils.import_string('datetime.date') is datetime.date
    assert utils.import_string('datetime') is datetime
    assert utils.import_string('sea.app:Sea') is Sea
    m = utils.import_string('app.servicers:GreeterServicer')
    from app.servicers import GreeterServicer
    assert m is GreeterServicer
    with pytest.raises(ImportError):
        utils.import_string('notexist')
    with pytest.raises(ImportError):
        utils.import_string('datetime.XXXXXXXXXXXX')


def test_cached_property():
    class ForTest:

        def __init__(self):
            self.count = 0

        @utils.cached_property
        def cached_count(self):
            return self.count

    assert isinstance(ForTest.cached_count, utils.cached_property)
    ins = ForTest()
    assert ins.cached_count == 0
    ins.count = 10
    assert ins.cached_count == 0
