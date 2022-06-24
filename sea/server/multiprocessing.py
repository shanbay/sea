import contextlib
import glob
import multiprocessing
import os
import signal
import socket
import time
from concurrent import futures
from typing import List

import grpc

from sea import signals


class Server:
    """sea multiprocessing server implementation

    :param app: application instance
    """

    def __init__(self, app):
        # application instance
        self.app = app
        # worker process number
        self.worker_num: int = self.app.config["GRPC_WORKERS"]
        # worker thread number
        self.thread_num: int = self.app.config.get("GRPC_THREADS")
        self.host: str = self.app.config["GRPC_HOST"]
        self.port: int = self.app.config["GRPC_PORT"]
        # slave worker refs, master node contains all slave workers refs
        self.workers: List[multiprocessing.Process] = []
        self._stopped: bool = False
        # slave worker server instance ref
        self.server: grpc.Server = None

    def _run_server(self, bind_address):
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=self.thread_num),
            options=[
                (
                    "grpc.so_reuseport",
                    1,
                ),  # multiprocessing worker must reuse port to pass between processes.
            ],
        )
        self.server = server  # set server in slave process

        for _, (add_func, servicer) in self.app.servicers.items():
            add_func(servicer(), server)
        server.add_insecure_port(bind_address)
        server.start()

        signals.server_started.send(self)

        # hang up here, to make slave run always
        server.wait_for_termination()

    def _run_prometheus_http_server(self):
        """Run prometheus_client built-in http server.

        Duing to prometheus_client multiprocessing details,
        PROMETHEUS_MULTIPROC_DIR must set in environment variables."""
        if not self.app.config["PROMETHEUS_SCRAPE"]:
            return

        from prometheus_client import REGISTRY, start_http_server
        from prometheus_client.multiprocess import MultiProcessCollector

        MultiProcessCollector(REGISTRY)
        start_http_server(self.app.config["PROMETHEUS_PORT"])

    def _clean_prometheus(self):
        if not self.app.config["PROMETHEUS_SCRAPE"]:
            return
        dir = os.getenv("PROMETHEUS_MULTIPROC_DIR")
        self.app.logger.info(f"clean prometheus dir {dir}")
        for f in glob.glob(os.path.join(dir, "*")):
            os.remove(f)

    def run(self):
        self._run_prometheus_http_server()

        self._register_signals()

        with _reserve_address_port(self.host, self.port) as bind_address:
            for _ in range(self.worker_num):
                worker = multiprocessing.Process(
                    target=self._run_server, args=(bind_address,)
                )
                worker.start()
                self.workers.append(worker)
            for worker in self.workers:
                worker.join()

        self._clean_prometheus()

        return True

    def _register_signals(self):
        signal.signal(signal.SIGINT, self._stop_handler)
        signal.signal(signal.SIGHUP, self._stop_handler)
        signal.signal(signal.SIGTERM, self._stop_handler)
        signal.signal(signal.SIGQUIT, self._stop_handler)

    def _stop_handler(self, signum, frame):
        grace = max(self.app.config.get("GRPC_GRACE", 0), 5)

        if self._stopped:
            self.app.logger.debug(
                "stop signal has received, ignore duplicated function signal"
            )
            return
        self._stopped = True

        if not self.server:
            # master
            self.app.logger.warning(
                "master process received signal {}, sleep {} to wait slave done".format(
                    signum, grace
                )
            )
            signals.server_stopped.send(self)

            # master process sleep to wait slaves end their lives
            time.sleep(grace)

            # kill the slave process which don't wanna die
            for worker in self.workers:
                if worker.is_alive():
                    self.app.logger.warning(
                        "master found process {} still alive after {} timeout".format(
                            worker.pid, grace
                        )
                    )
                    # compatitable with 3.6 and before
                    if callable(getattr(worker, "kill", None)):
                        worker.kill()
                    else:
                        os.kill(worker.pid, signal.SIGKILL)
            self.app.logger.warning("master exit")
        else:
            # slave
            signals.server_stopped.send(self)
            self.app.logger.warning(
                "slave process received signal {}, try to stop process".format(signum)
            )
            # slave process sleep less 3s to make grace more reliable
            self.server.stop(grace - 3)
            time.sleep(grace - 3)


@contextlib.contextmanager
def _reserve_address_port(host, port):
    """Find and reserve a port for all subprocesses to use."""

    from ipaddress import IPv6Address, ip_address

    ipv6 = False
    if host and type(ip_address(host)) is IPv6Address:
        ipv6 = True

    sock = socket.socket(
        socket.AF_INET6 if ipv6 else socket.AF_INET, socket.SOCK_STREAM
    )

    # ENABLE SO_REUSEPORT
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")

    sock.bind((host, port))
    try:
        if ipv6:
            yield "[{0}]:{1}".format(*sock.getsockname())
        else:
            yield "{0}:{1}".format(*sock.getsockname())
    finally:
        sock.close()
