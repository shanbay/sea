import signal
import asyncio
from concurrent import futures

import grpc
from grpc_reflection.v1alpha import reflection

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
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=self.workers))
        self.server.add_insecure_port("{}:{}".format(self.host, self.port))
        self._stopped = False

    async def run(self):
        self.app.logger.warning("Starting server...")
        # run prometheus client
        if self.app.config["PROMETHEUS_SCRAPE"]:
            from prometheus_client import start_http_server

            self.app.logger.warning(f'Starting prometheus client...{self.app.config["PROMETHEUS_PORT"]}')
            start_http_server(self.app.config["PROMETHEUS_PORT"])
        # register reflection service
        if self.app.config.get("GRPC_REFLECTION_SERVICES"):
            reflection.enable_server_reflection((reflection.SERVICE_NAME, *self.app.config["GRPC_REFLECTION_SERVICES"]), self.server)
        # run grpc server
        for _, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), self.server)
        await self.server.start()
        signals.server_started.send(self)
        self.register_signal()

        await self.server.wait_for_termination()
        # while not self._stopped:
        #     await asyncio.sleep(1)
        # signals.server_stopped.send(self)
        # return True

    def register_signal(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    async def _stop_handler(self):
        self.app.logger.warning("Stopping server...")
        grace = self.app.config["GRPC_GRACE"]
        await self.server.stop(grace)
        await asyncio.sleep(grace or 1)
        self._stopped = True
