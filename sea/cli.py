import sys
import os
import argparse
import code
import abc

from sea import create_app
from sea.server import Server


class TaskManager:
    pass


class AbstractCommand(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def opt(self, subparsers):
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, args):
        raise NotImplementedError


class ServerCmd(AbstractCommand):
    def opt(self, subparsers):
        p = subparsers.add_parser(
            'server', aliases=['s'], help='Run Server')
        p.add_argument(
            '-b', '--host', required=True,
            help='published host which others can connect through')
        return p

    def run(self, args):
        app = create_app(args.workdir)
        s = Server(app, args.host)
        return s.run()


class ConsoleCmd(AbstractCommand):
    def opt(self, subparsers):
        p = subparsers.add_parser(
            'console', aliases=['c'], help='Run Console')
        return p

    def run(self, args):
        banner = """
        [Sea Console]:
        the following vars are included:
        `app` (the current app)
        """
        app = create_app(args.workdir)
        ctx = {'app': app}
        try:
            from IPython import embed
            return embed(banner1=banner, user_ns=ctx)
        except ImportError:
            return code.interact(banner, local=ctx)


class NewCmd(AbstractCommand):

    def opt(self, subparsers):
        p = subparsers.add_parser(
            'new', aliases=['n'], help='Create Sea Project')
        p.add_argument(
            'project', help='project name')
        return p

    def run(self, args):
        pass


class TaskCmd(AbstractCommand):

    def opt(self, subparsers):
        p = subparsers.add_parser(
            'invoke', help='Invoke Sea Tasks')
        p.add_argument(
            'task', help='task name')
        return p

    def run(self, args):
        pass


def main():
    root = argparse.ArgumentParser('sea')
    root.add_argument(
        '-w', '--workdir', default=os.getcwd(),
        help='set work dir')
    subparsers = root.add_subparsers()
    for k, v in globals().items():
        if k.endswith('Cmd') and issubclass(v, AbstractCommand):
            cmd = v()
            cmd.opt(subparsers).set_defaults(handler=cmd.run)

    args = sys.argv[1:]
    args = root.parse_args(args)
    return args.handler(args)
