import pytest

from sea.extensions import AbstractExtension


def test_abs_extension():
    class ErrorExtension(AbstractExtension):
        pass

    with pytest.raises(TypeError):
        ErrorExtension()

    class Extension(AbstractExtension):
        def init_app(self, app):
            return app

    e = Extension()
    with pytest.raises(NotImplementedError):
        AbstractExtension.init_app(e, 'x')
    app = e.init_app('hello')
    assert app == 'hello'
