import json
import os.path

from sea.app import Sea
from sea.config import ConfigAttribute, Config


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
    s = repr(app.config)
    assert '<Config' in s


def test_config_attribute():
    class App:
        x = ConfigAttribute('n_x', json.loads)

    assert type(App.x) == ConfigAttribute
    a = App()
    a.config = Config('root', {'n_x': json.dumps({'foo': 'bar'})})
    assert 'foo' in a.x
    a.x = json.dumps({'a': 1})
    assert 'a' in a.x
