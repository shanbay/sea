import sys
import os
import argparse
import code
import abc

from sea import create_app
from sea.server import Server
from sea.utils import import_string

from jinja2 import Environment, FileSystemLoader


class TaskOption:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class TaskManager:

    def __init__(self):
        self.tasks = {}

    def task(self, name):
        def wrapper(func):
            self.tasks[name] = func
            return func
        return wrapper

    def option(self, *args, **kwargs):
        def wrapper(func):
            opts = getattr(func, 'opts', [])
            if not opts:
                func.opts = opts
            opts.append(TaskOption(*args, **kwargs))
            return func
        return wrapper

    def __getitem__(self, name):
        return self.tasks[name]


taskm = TaskManager()


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

    def run(self, args, extra=[]):
        if extra:
            raise ValueError
        app = create_app(args.workdir)
        s = Server(app, args.host)
        return s.run()


class ConsoleCmd(AbstractCommand):
    def opt(self, subparsers):
        p = subparsers.add_parser(
            'console', aliases=['c'], help='Run Console')
        return p

    def run(self, args, extra=[]):
        if extra:
            raise ValueError
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

    PACKAGE_DIR = os.path.dirname(__file__)
    TMPLPATH = os.path.join(PACKAGE_DIR, 'template')
    IGNORED_DIRECTORIES = ['__pycache__']

    def opt(self, subparsers):
        p = subparsers.add_parser(
            'new', aliases=['n'], help='Create Sea Project')
        p.add_argument('project', help='project name')
        p.add_argument(
            '--skip-git', action='store_true',
            help='skip add git files and run git init')
        p.add_argument(
            '--skip-orator', action='store_true', help='skip orator')
        p.add_argument(
            '--skip-consul', action='store_true', help='skip consul')
        return p

    def run(self, args, extra=[]):
        if extra:
            raise ValueError
        dest_path = '{}/{}'.format(os.getcwd(), args.project)
        env = Environment(loader=FileSystemLoader(self.TMPLPATH))

        # skip some unneeded files
        skip_files = []
        if args.__dict__.get('skip_git', False):
            skip_files.append('.gitignore')
        if args.__dict__.get('skip_orator', False):
            skip_files.append('orator.tpl')
        if args.__dict__.get('skip_consul', False):
            skip_files.append('consul.tpl')

        # traverse all files in template dir
        for dir_path, dirs, filenames in os.walk(self.TMPLPATH):
            dirs[:] = [d for d in dirs if d not in self.IGNORED_DIRECTORIES]
            for filename in filenames:
                if filename not in skip_files:
                    rel_path = os.path.join(
                        os.path.relpath(dir_path, self.TMPLPATH), filename)
                    template = env.get_template(rel_path)
                    dest_file = os.path.join(dest_path,
                                             rel_path).replace('.tpl', '.py')
                    # create the parentdir if not exists
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    print(dest_file)
                    with open(dest_file, 'w') as f:
                        f.write(template.render(**args.__dict__))


class TaskCmd(AbstractCommand):

    def _load_plugin_tasks(self):
        import pkg_resources
        for ep in pkg_resources.iter_entry_points('sea.tasks'):
            ep.load()
        return True

    def _load_app_tasks(self, app):
        root = os.path.join(app.root_path, 'tasks')
        for m in os.listdir(root):
            if m != '__init__.py' and \
                    m.endswith('.py') and \
                    os.path.isfile(os.path.join(root, m)):
                import_string('tasks.{}'.format(m[:-3]))
        return True

    def opt(self, subparsers):
        p = subparsers.add_parser(
            'invoke', aliases=['i'], help='Invoke Sea Tasks')
        p.add_argument(
            'task', help='task name')
        return p

    def run(self, args, extra=[]):
        app = create_app(args.workdir)
        self._load_plugin_tasks()
        self._load_app_tasks(app)
        global taskm
        func = taskm[args.task]
        opts = getattr(func, 'opts', [])
        parser = argparse.ArgumentParser('seatask')
        for opt in opts:
            parser.add_argument(*opt.args, **opt.kwargs)
        return func(**vars(parser.parse_args(extra)))


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
    args, extra = root.parse_known_args(args)
    return args.handler(args, extra)
