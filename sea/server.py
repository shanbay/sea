import signal
import sys
from concurrent import futures
import grpc


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Server:

    def __init__(self, app):
        self.app = app
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.app.config.get('WORKERS')))
        regconf = self.app.config.get_namespace('REGISTER_')
        self.register = regconf['class'](
            self.app.extensions[regconf['client']])

    def run(self, port):
        port = str(port)
        for name, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), self.server)
            self.register.register(name, port)
        self.server.add_insecure_port('[::]:{}'.format(port))
        self.server.start()

        self.register_signal()

        import time
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)

    def register_signal(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    def _stop_handler(self, signum, frame):
        self.server.stop(0)
        sys.exit(0)
