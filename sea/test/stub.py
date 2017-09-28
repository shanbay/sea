class Context():
    def __init__(self):
        self.code = None
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


def _handler_wrapper(handler):
    def wrapped(msg, metadata=None):
        ctx = Context()
        ctx.initial_metadata(metadata)
        return handler(msg, ctx)
    return wrapped


class Stub():

    def __init__(self, servicer=None):
        self.servicer = servicer

    def __getattr__(self, handler):
        return _handler_wrapper(getattr(self.servicer, handler))

