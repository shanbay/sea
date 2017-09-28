class Stub(object):

    class BaseContext():
        def __init__(self):
            self.code = None
            self.details = None

        def set_code(self, code):
            self.code = code

        def set_details(self, details):
            self.details = details

    def __init__(self, servicer=None):
        self.servicer = servicer
        self.context = self.BaseContext()

    def __getattr__(self, item):
        func = getattr(self.servicer, item)
        func.__func__.__defaults__ = (self.context,)
        return func
