import pytest
import os.path

from sea import app
from sea.servicer import MetaServicer

import grpc_mock


class PersonServicer(grpc_mock.PersonServicer, metaclass=MetaServicer):
    DEFAULT_MSG_CLASS = str

    def get_a_person(self, request, context):
        return


def test_sea():
    _app = app.Sea(os.path.dirname(__file__))
    assert not _app.debug
    assert not _app.testing
    assert _app.extensions == {}
    assert _app.servicers == {}

    class C(object):
        DEBUG = True
        TESTING = True

    _app.config.from_object(C)
    assert _app.debug
    assert _app.testing

    _app.register_servicer(PersonServicer)
    assert 'PersonServicer' in _app.servicers
    servicer = _app.servicers['PersonServicer']
    assert isinstance(servicer, tuple)
    assert servicer == (grpc_mock.add_PersonServicer_to_server, PersonServicer)
    with pytest.raises(RuntimeError):
        _app.register_servicer(PersonServicer)

