import sys
import os
import os.path
import subprocess


def main():
    args = sys.argv[1:]
    env = os.environ.get('SEA_ENV', 'development')
    dbconfig = os.path.join(
        os.getcwd(), 'configs/{}/orator.py'.format(env))
    args = ['orator', '-c', dbconfig] + args
    if sys.version_info.minor < 5:
        return subprocess.check_output(args, stderr=subprocess.STDOUT)
    else:
        return subprocess.run(
                    args, check=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT
                    ).stdout
