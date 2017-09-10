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
