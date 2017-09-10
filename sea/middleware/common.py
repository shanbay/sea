import datetime
import grpc

from sea import exceptions
from sea.pb2 import default_pb2
from .base import BaseMiddleware


class GuardMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        try:
            return self.handler(servicer, request, context)
        except Exception as e:
            self.app.logger.exception(
                str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal Error Occured')
            return default_pb2.Empty()


class RpcErrorMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        try:
            return self.handler(servicer, request, context)
        except exceptions.RpcException as e:
            context.set_code(e.code)
            context.set_details(e.details)
            return default_pb2.Empty()


class ServiceLogMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        start_at = datetime.datetime.now(self.app.tz)
        response = self.handler(servicer, request, context)
        finish_at = datetime.datetime.now(self.app.tz)
        delta = finish_at - start_at
        self.app.logger.info(
            '[{}] {}.{} Called. Processed in {}s'.format(
                start_at.isoformat(),
                servicer.__class__.__name__,
                self.origin_handler.__name__,
                delta.total_seconds()
            )
        )
        return response
