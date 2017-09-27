import grpc
import json


class ConfigException(RuntimeError):
    pass


class RpcException(Exception):

    code = None
    details = None

    def __init__(self, message=None, *args, **kwargs):
        if isinstance(message, (list, dict)):
            message = json.dumps(
                message, default=str, ensure_ascii=False)
        if not isinstance(message, str):
            message = str(message)
        if message is not None:
            self.details = message
        super().__init__(message, *args, **kwargs)


class NotFoundException(RpcException):

    code = grpc.StatusCode.NOT_FOUND
    details = 'Not Found'


class BadRequestException(RpcException):

    code = grpc.StatusCode.INVALID_ARGUMENT
    details = 'Invalid Argument'
