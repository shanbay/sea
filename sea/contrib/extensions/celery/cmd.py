import sys

from celery.__main__ import main as celerymain

from sea.cli import jobm


@jobm.job('celery', proxy=True, help='invoke celery cmds')
def main(argv):
    sys.argv = ['celery'] + argv + \
        ['-A', 'app.extensions:celeryapp']
    return celerymain()
