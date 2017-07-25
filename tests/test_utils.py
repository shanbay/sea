import pytest
from sea import utils


def test_import_string():
    from sea.app import Sea
    import datetime
    assert utils.import_string('datetime.date') is datetime.date
    assert utils.import_string('datetime.date') is datetime.date
    assert utils.import_string('XXXXXXXXXXXX', True) is None
    assert utils.import_string('datetime.XXXXXXXXXXXX', True) is None
    assert utils.import_string('sea.app.Sea') is Sea
    pytest.raises(ImportError, utils.import_string, 'XXXXXXXXXXXXXXXX')
    pytest.raises(ImportError, utils.import_string, 'cgi.XXXXXXXXXX')
