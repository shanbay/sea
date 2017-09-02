import pytest
import logging
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


def test_logger_has_level_handler():
    l1 = logging.getLogger('testapp')
    l1.setLevel(logging.ERROR)
    l2 = logging.getLogger('testapp.sub')
    l3 = logging.getLogger('testapp.nest')
    l3.propagate = False

    assert not utils.logger_has_level_handler(l2)
    assert not utils.logger_has_level_handler(l3)

    h1 = logging.StreamHandler()
    h1.setLevel('INFO')
    l1.addHandler(h1)
    assert utils.logger_has_level_handler(l2)
    assert not utils.logger_has_level_handler(l3)
    l3.setLevel(logging.ERROR)
    assert not utils.logger_has_level_handler(l3)

    l2.setLevel(logging.DEBUG)
    assert not utils.logger_has_level_handler(l2)
    h2 = logging.StreamHandler()
    h2.setLevel(logging.DEBUG)
    l2.addHandler(h2)
    assert utils.logger_has_level_handler(l2)

    h3 = logging.StreamHandler()
    h3.setLevel(logging.DEBUG)
    l3.addHandler(h3)
    assert utils.logger_has_level_handler(l3)
