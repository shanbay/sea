import json
import os

from sea.config import ConfigAttribute, Config


def test_config_from_class():
    class Base(object):
        TEST_KEY = 'foo'
        TEST_VALUE = 'bar'

    class Test(Base):
        TESTING = True

    config = Config('.', {'TESTING': False})

    assert config['TESTING'] is False
    config.from_object(Test)
    assert config['TESTING'] is True

    assert config['TEST_KEY'] == 'foo'
    assert 'TestConfig' not in config
    d = config.get_namespace('TEST_')
    assert 'key' in d
    assert 'value' in d
    d = config.get_namespace(
        'TEST_', lowercase=False, trim_namespace=False)
    assert 'TEST_KEY' in d
    s = repr(config)
    assert '<Config' in s


def test_config_load_from_env():
    config = Config('.', {'KEY_INT': 1, 'KEY_STR': 'str', 'KEY_BOOL': True})
    os.environ['KEY_INT'] = "300"
    os.environ['KEY_STR'] = "TESTING"
    os.environ['KEY_BOOL'] = "False"

    assert config['KEY_INT'] == 1
    assert config['KEY_STR'] == 'str'
    assert config['KEY_BOOL'] == True  # noqa

    config.load_config_from_env()
    assert config['KEY_INT'] == 300
    assert config['KEY_STR'] == 'TESTING'
    assert config['KEY_BOOL'] == False  # noqa

    os.environ['TEST'] = 'True'
    config.load_config_from_env()
    assert 'TEST' not in config


def test_config_attribute():
    class App:
        x = ConfigAttribute('n_x', json.loads)

    assert type(App.x) == ConfigAttribute
    a = App()
    a.config = Config('root', {'n_x': json.dumps({'foo': 'bar'})})
    assert 'foo' in a.x
    a.x = json.dumps({'a': 1})
    assert 'a' in a.config['n_x']
