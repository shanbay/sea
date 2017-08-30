from sea.middleware import BaseMiddleware


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
    return context


def test_base_middleware():
    h = FakeInMiddleware(handler)
    h = FakeOutMiddleware(h)
    h = BaseMiddleware(h)
    ret = h(None, None, {'msg': ''})
    assert ret['msg'].strip().split('\n') == [
        'Out.before_handler',
        'In.before_handler',
        'In.after_handler',
        'Out.after_handler'
        ]
