import abc


class AbstractExtension(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def init_app(self, app):
        raise NotImplementedError
