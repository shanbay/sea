import logging
import warnings
from pprint import pformat

import grpc
import pendulum

from sea import exceptions
from sea.format import msg2dict
from sea.pb2 import default_pb2


class BaseMiddleware:
    def __init__(self, app, handler, origin_handler):
        self.app = app
        self.handler = handler
        self.origin_handler = origin_handler

    def __call__(self, servicer, request, context):
        request, context = self.before_handler(servicer, request, context)
        response = self.handler(servicer, request, context)
        return self.after_handler(servicer, response)

    def before_handler(self, servicer, request, context):
        return request, context

    def after_handler(self, servicer, response):
        return response


class GuardMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        try:
            return self.handler(servicer, request, context)
        except Exception as e:
            self.app.logger.exception(str(e), exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal Error Occurred')
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
    def __init__(self, app, handler, origin_handler):
        super().__init__(app, handler, origin_handler)
        is_production = (app.env == 'production')
        log_level = app.logger.getEffectiveLevel()
        is_low_log_level = (app.debug or log_level < logging.WARNING)
        if is_production and is_low_log_level:
            warnings.warn(
                'Using ServiceLogMiddleware in production with a low log_level'
                '(app.debug is True or log_level < logging.WARNING) '
                'is definitely not recommended!'
            )

    def __call__(self, servicer, request, context):
        if self.app.debug:
            return self._debug_log(servicer, request, context)
        return self._normal_log(servicer, request, context)

    def _debug_log(self, servicer, request, context):
        start_at = pendulum.now(self.app.tz)
        self.app.logger.info(
            '[%s] %s.%s was Called.\nRequest:\n%s', start_at.isoformat(),
            servicer.__class__.__name__, self.origin_handler.__name__,
            pformat(msg2dict(request, including_default_value_fields=True)))
        response = self.handler(servicer, request, context)
        finish_at = pendulum.now(self.app.tz)
        delta = finish_at - start_at
        self.app.logger.info(
            'Processed in %ss\nResponse:\n%s', delta.total_seconds(),
            pformat(msg2dict(response, including_default_value_fields=True)))

        return response

    def _normal_log(self, servicer, request, context):
        start_at = pendulum.now(self.app.tz)
        response = self.handler(servicer, request, context)
        finish_at = pendulum.now(self.app.tz)
        delta = finish_at - start_at
        self.app.logger.info('[{}] {}.{} Called. Processed in {}s'.format(
            start_at.isoformat(), servicer.__class__.__name__,
            self.origin_handler.__name__, delta.total_seconds()))

        return response
