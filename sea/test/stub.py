import grpc


class Context():
    def __init__(self):
        self.code = grpc.StatusCode.OK
        self.details = None
        self.metadata = None

    def set_code(self, code):
        self.code = code

    def set_details(self, details):
        self.details = details

    def initial_metadata(self, metadata):
        self.metadata = metadata

    def invocation_metadata(self):
        return self.metadata


class Stub():

    def __init__(self, servicer=None):
        self.servicer = servicer

    def __getattr__(self, handler):
        return self._handler_wrapper(getattr(self.servicer, handler))

    def _handler_wrapper(self, handler):
        def wrapped(msg, metadata=None):
            self.ctx = Context()
            self.ctx.initial_metadata(metadata)
            return handler(msg, self.ctx)
        return wrapped
