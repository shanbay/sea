import sys

from celery.__main__ import main as celerymain

from sea.cli import jobm


@jobm.job('async_task', proxy=True, help='invoke celery cmds for async tasks')
def async_task(argv):
    sys.argv = ['celery'] + argv + \
        ['-A', 'app.extensions:async_task']
    return celerymain()

@jobm.job('bus', proxy=True, help='invoke celery cmds for bus')
def bus(argv):
    sys.argv = ['celery'] + argv + \
        ['-A', 'app.extensions:bus']
    return celerymain()
