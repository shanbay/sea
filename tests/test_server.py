import os
import signal
import time
from multiprocessing import Process

import sea
from sea.server import Server
from sea.register import ConsulRegister


def test_server():
    os.environ.setdefault('SEA_ENV', 'testing')
    app = sea.create_app('.')
    s = Server(app)

    assert isinstance(s.register, ConsulRegister)

    p = Process(target=s.run, args=('10241',))
    p.start()

    assert p.is_alive()
    os.kill(p.pid, signal.SIGUSR1)
    assert p.is_alive()
    os.kill(p.pid, signal.SIGINT)
    time.sleep(1)
    assert not p.is_alive()
