import signal
import time
from concurrent import futures

import grpc

from sea import signals


class Server:
    """sea server implements

    :param app: application instance
    """

    def __init__(self, app):
        self.app = app
        self.workers = self.app.config["GRPC_WORKERS"]
        self.host = self.app.config["GRPC_HOST"]
        self.port = self.app.config["GRPC_PORT"]
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.workers))
        self.server.add_insecure_port("{}:{}".format(self.host, self.port))
        self._stopped = False

    def run(self):
        # run prometheus client
        if self.app.config["PROMETHEUS_SCRAPE"]:
            from prometheus_client import start_http_server

            start_http_server(self.app.config["PROMETHEUS_PORT"])
        # run grpc server
        for name, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), self.server)
        self.server.start()
        signals.server_started.send(self)
        self.register_signal()
        while not self._stopped:
            time.sleep(1)
        signals.server_stopped.send(self)
        return True

    def register_signal(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    def _stop_handler(self, signum, frame):
        grace = self.app.config["GRPC_GRACE"]
        self.server.stop(grace)
        time.sleep(grace or 1)
        self._stopped = True
