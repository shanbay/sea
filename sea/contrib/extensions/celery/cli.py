import sys
import os
import subprocess

import sea


app = sea.create_app(os.getcwd())
celery = app.extensions['celery']


def main():
    args = sys.argv[1:]
    args = ['celery'] + args + \
        ['-A', 'sea.contrib.extensions.celery.cli:celery']
    return subprocess.check_output(args, stderr=subprocess.STDOUT)
