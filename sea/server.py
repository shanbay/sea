import signal
import time
import logging
from concurrent import futures
import grpc
import blinker


started = blinker.signal('server_started')
stopped = blinker.signal('server_stopped')


class Server:
    """sea server implements

    :param app: application instance
    :param publish_host: publish host
    """

    def __init__(self, app, publish_host):
        self.app = app
        self.setup_logger()
        self.workers = self.app.config.get('GRPC_WORKERS')
        self.host = self.app.config.get('GRPC_HOST')
        self.port = self.app.config.get('GRPC_PORT')
        self.publish_host = publish_host
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=self.workers))
        self.server.add_insecure_port(
            '{}:{}'.format(self.host, self.port))
        self._stopped = False

    def run(self):
        """run the server
        """
        for name, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), self.server)
        self.server.start()
        started.send(self)
        self.register_signal()
        while not self._stopped:
            time.sleep(1)
        stopped.send(self)
        return True

    def setup_logger(self):
        fmt = self.app.config['GRPC_LOG_FORMAT']
        lvl = self.app.config['GRPC_LOG_LEVEL']
        h = self.app.config['GRPC_LOG_HANDLER']
        h.setFormatter(logging.Formatter(fmt))
        logger = logging.getLogger()
        logger.setLevel(lvl)
        logger.addHandler(h)

    def register_signal(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    def _stop_handler(self, signum, frame):
        self.server.stop(0)
        self._stopped = True
