import grpc


class ConfigException(RuntimeError):
    pass


class RpcException(Exception):

    code = None
    details = None

    def __init__(self, message, *args, **kwargs):
        self.details = message
        super().__init__(message, *args, **kwargs)


class NotFoundException(RpcException):

    code = grpc.StatusCode.NOT_FOUND
    details = 'Not Found'


class BadRequestException(RpcException):

    code = grpc.StatusCode.INVALID_ARGUMENT
    details = 'Invalid Argument'
