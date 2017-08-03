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
    s = Server(app, '127.0.0.1')

    assert isinstance(s.register, ConsulRegister)
    assert not s._stopped

    def _term(pid):
        time.sleep(0.5)
        os.kill(pid, signal.SIGINT)

    p = Process(target=_term, args=(os.getpid(),))
    p.start()
    assert s.run()
    assert s._stopped
