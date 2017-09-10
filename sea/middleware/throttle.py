from sea.datatypes import KeyExpiredDict
from .base import BaseMiddleware
from sea.pb2 import default_pb2
from sea.utils import Singleton


class ThrottleMiddleware(BaseMiddleware, metaclass=Singleton):

    def __init__(self, app, handler, origin_handler):
        try:
            config = app.config['THROTTLE']
            self.storage = KeyExpiredDict(config['store_max_len'])
            self.limit = config['limit']
            self.duration = config['duration']
        except KeyError:
            raise Exception("You must config throttle before use")
        super().__init__(app, handler, origin_handler)

    def _enalbe_pass(self, key):
        result = self.storage.get(key)
        if result is None:
            self.storage.set(key, 1, seconds=self.duration)
        else:
            count = int(result)
            if count < self.limit:
                self.storage.incr(key)
            else:
                self.storage.expire(key, self.duration)
                return False
        return True

    def __call__(self, servicer, request, context):
        # ipv6:[::1]:12345
        address = ':'.join(context.peer().split(':')[:-1])
        if self._enalbe_pass(address):
            return self.handler(servicer, request, context)
        return default_pb2.Empty()
