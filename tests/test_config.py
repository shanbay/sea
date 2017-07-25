import os.path

from sea.app import Sea


def test_config_from_class():
    class Base(object):
        TEST_KEY = 'foo'
        TEST_VALUE = 'bar'

    class Test(Base):
        TESTING = True

    path = os.path.join(os.path.dirname(__file__), '..')
    app = Sea(os.path.abspath(path))
    app.config.from_object(Test)

    assert app.testing
    assert app.config['TEST_KEY'] == 'foo'
    assert 'TestConfig' not in app.config
    d = app.config.get_namespace('TEST_')
    assert 'key' in d
    assert 'value' in d
    d = app.config.get_namespace(
        'TEST_', lowercase=False, trim_namespace=False)
    assert 'TEST_KEY' in d
