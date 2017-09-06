import sys
import os

from celery.__main__ import main as celerymain

import sea


def main():
    sea.create_app(os.getcwd())

    args = sys.argv[1:]
    args = ['celery'] + args + \
        ['-A', 'app.extensions:celeryapp']
    sys.argv = args
    return celerymain()
