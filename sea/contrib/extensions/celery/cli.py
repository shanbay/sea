import sys
import os
from celery.__main__ import main as celerymain

import sea


app = sea.create_app(os.getcwd())
celery = app.extensions['celery']


def main():
    args = sys.argv[1:]
    args = ['celery'] + args + \
        ['-A', 'sea.contrib.extensions.celery.cli:celery']
    sys.argv = args
    sys.exit(celerymain())
