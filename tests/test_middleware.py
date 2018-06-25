import logging
import warnings
from unittest import mock

from sea.middleware import (BaseMiddleware, GuardMiddleware,
                            ServiceLogMiddleware)
from sea.pb2 import default_pb2


class FakeInMiddleware(BaseMiddleware):
    def before_handler(self, servicer, request, context):
        context['msg'] += 'In.before_handler\n'
        return request, context

    def after_handler(self, servicer, response):
        response['msg'] += 'In.after_handler\n'
        return response


class FakeOutMiddleware(BaseMiddleware):
    def before_handler(self, servicer, request, context):
        context['msg'] += 'Out.before_handler\n'
        return request, context

    def after_handler(self, servicer, response):
        response['msg'] += 'Out.after_handler\n'
        return response


def handler(servicer, request, context):
    if request is not None:
        raise ValueError
    return context


def test_base_middleware(app):

    h = FakeInMiddleware(app, handler, handler)
    h = FakeOutMiddleware(app, h, handler)
    h = BaseMiddleware(app, h, handler)
    h = GuardMiddleware(app, h, handler)

    ret = h(None, None, {'msg': ''})
    assert ret['msg'].strip().split('\n') == [
        'Out.before_handler',
        'In.before_handler',
        'In.after_handler',
        'Out.after_handler'
    ]

    ctx = mock.MagicMock()
    ret = h(None, 1, ctx)
    assert ctx.set_code.called


def test_service_log_middleware(app):
    app.debug = True
    app.env = 'production'
    with warnings.catch_warnings(record=True) as w:
        h = ServiceLogMiddleware(
            app=app,
            handler=lambda servicer, request, context: default_pb2.Empty(),
            origin_handler=handler
        )
        h(None, default_pb2.Empty(), {'msg': ''})
        assert len(w) == 1
        assert 'ServiceLogMiddleware' in str(w[0].message)
