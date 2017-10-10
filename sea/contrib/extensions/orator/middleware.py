import grpc

from sea.pb2 import default_pb2
from sea.middleware import BaseMiddleware
from orator.exceptions.orm import (
    ModelNotFound, RelatedClassNotFound, ValidationError)


class OratorExceptionMiddleware(BaseMiddleware):
    def __call__(self, servicer, request, context):
        try:
            return self.handler(servicer, request, context)
        except (ModelNotFound, RelatedClassNotFound) as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(str(e))
        except ValidationError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
        return default_pb2.Empty()
