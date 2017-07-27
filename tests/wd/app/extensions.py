from sea.extensions import AbstractExtension


class Cache(AbstractExtension):

    def init_app(self, app):
        return app


cache = Cache()
