from unittest import mock

from sea.middleware import ThrottleMiddleware


def test_base_middleware(app):
    handler = mock.MagicMock()
    h = ThrottleMiddleware(app, handler, handler)
    context = type('Context', (object,), {'peer': lambda: "ipv6:[::1]:123456"})
    h(None, None, context)
    assert handler.called
    handler.reset_mock()
    h(None, None, context)
    assert handler.called
    handler.reset_mock()
    h(None, None, context)
    assert not handler.called
