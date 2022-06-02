import contextlib
import multiprocessing
import signal
import socket
import time
import logging
from concurrent import futures
import grpc

from sea import signals

"""
GRPC_WORKERS
GRPC_THREADS
GRPC_HOST
GRPC_PORT
GRPC_GRACE

GRPC_LOG_FORMAT
GRPC_LOG_LEVEL
GRPC_LOG_HANDLER
"""


class Server:
    """sea multiprocessing server implements

    :param app: application instance
    """

    def __init__(self, app):
        self.app = app
        self.worker_num = self.app.config['GRPC_WORKERS']
        self.thread_num = self.app.config.get('GRPC_THREADS', 1)
        self.host = self.app.config['GRPC_HOST']
        self.port = self.app.config['GRPC_PORT']
        self.workers = []
        self._stopped = False

        self.server = None # slave process server object
    
    def _run_server(self, bind_address):
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.thread_num),
            options=[
                ("grpc.so_reuseport", 1),
                # ("grpc.use_local_subchannel_pool", 1),
            ],
        ) 
        for _, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), server)
        server.add_insecure_port(bind_address)
        server.start()
        self.server = server # set server in slave process

        signals.server_started.send(self)
        server.wait_for_termination()

    def run(self):
        # # run prometheus client
        # if self.app.config['PROMETHEUS_SCRAPE']:
        #     from prometheus_client import start_http_server
        #     start_http_server(self.app.config['PROMETHEUS_PORT'])
        
        self.register_signal()

        with _reserve_address_port(self.host, self.port) as port:
            bind_address = "{}:{}".format(self.host, self.port)
            for _ in range(self.worker_num):
                worker = multiprocessing.Process(target=self._run_server, args=(bind_address,))
                worker.start()
                self.workers.append(worker)
            for worker in self.workers:
                worker.join()
        
        return True


    def register_signal(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    def _stop_handler(self, signum, frame):
        grace = max(self.app.config['GRPC_GRACE'], 5) if self.app.config['GRPC_GRACE'] else 5
        if not self.server:
            self.app.logger.warning("master process received signal {}, sleep {} to wait slave done".format(signum, grace))

            # master process sleep to wait slaves end their lives
            time.sleep(grace)

            # kill the slave process which don't wanna die
            for worker in self.workers:
                if worker.is_alive():
                    self.app.logger.warning("master found process {} still alive after {} timeout".format(worker.pid, grace))
                    worker.kill()
            self.app.logger.warning("master exit")
        else:
            # slave process sleep less 3s to make grace more reliable
            self.app.logger.warning("slave process received signal {}, try to stop process".format(signum))
            self.server.stop(grace - 3)
            time.sleep(grace - 3)
            signals.server_stopped.send(self)

@contextlib.contextmanager
def _reserve_address_port(host, port):
    """Find and reserve a port for all subprocesses to use."""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(("", port))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()