from sea import exceptions
from sea.pb2 import default_pb2


class BaseMiddleware:
    def __init__(self, func):
        self.handler = func

    def __call__(self, servicer, request, context):
        request, context = self.before_handler(servicer, request, context)
        response = self.handler(servicer, request, context)
        return self.after_handler(servicer, response)

    def before_handler(self, servicer, request, context):
        return request, context

    def after_handler(self, servicer, response):
        return response


class RpcErrorMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        try:
            return self.handler(servicer, request, context)
        except exceptions.RpcException as e:
            context.set_code(e.code)
            context.set_details(e.details)
            return default_pb2.Empty()
