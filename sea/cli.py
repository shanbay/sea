import sys
import os
import argparse
import abc

from sea import create_app
from sea.server import Server
from sea.utils import import_string


class JobOption:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class JobManager:

    def __init__(self):
        self.jobs = {}

    def job(self, name, *args, **kwargs):
        def wrapper(func):
            func.job = JobOption(*args, **kwargs)
            self.jobs[name] = func
            return func
        return wrapper

    def option(self, *args, **kwargs):
        def wrapper(func):
            opts = getattr(func, 'opts', [])
            if not opts:
                func.opts = opts
            opts.append(JobOption(*args, **kwargs))
            return func
        return wrapper

    def __getitem__(self, name):
        return self.jobs[name]


jobm = JobManager()


class AbstractCommand(metaclass=abc.ABCMeta):

    APP_REQUIRED = True
    app = None

    def __init__(self):
        if self.APP_REQUIRED:
            self.app = create_app(os.getcwd())

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
        s = Server(self.app, args.host)
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
        ctx = {'app': self.app}
        try:
            from IPython import embed
            return embed(banner1=banner, user_ns=ctx)
        except ImportError:
            import code
            return code.interact(banner, local=ctx)


class NewCmd(AbstractCommand):

    APP_REQUIRED = False
    PACKAGE_DIR = os.path.dirname(__file__)
    TMPLPATH = os.path.join(PACKAGE_DIR, 'template')
    IGNORED_FILES = {
        'git': ['gitignore'],
        'consul': [],
        'orator': ['configs/development/orator.py.tmpl',
                   'configs/testing/orator.py.tmpl'
                   'app/models.py.tmpl',
                   'db/.keep'],
        'cache': [],
        'celery': ['configs/development/celery.py.tmpl',
                   'configs/testing/celery.py.tmpl',
                   'app/tasks.py.tmpl'],
    }

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
            '--skip-cache', action='store_true', help='skip cache')
        p.add_argument(
            '--skip-celery', action='store_true', help='skip celery')
        p.add_argument(
            '--skip-consul', action='store_true', help='skip consul')
        return p

    def _build_skip_files(self, args):
        skipped = set()
        for ignore_key in self.IGNORED_FILES.keys():
            if getattr(args, 'skip_' + ignore_key):
                for f in self.IGNORED_FILES[ignore_key]:
                    skipped.add(os.path.join(self.TMPLPATH, f))
        return skipped

    def _gen_project(self, path, skip=set(), ctx={}):
        import shutil
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader(self.TMPLPATH))
        for dirpath, dirnames, filenames in os.walk(self.TMPLPATH):
            for fn in filenames:
                src = os.path.join(dirpath, fn)
                if src not in skip:
                    relfn = os.path.relpath(src, self.TMPLPATH)
                    dst = os.path.join(path, relfn)
                    # create the parentdir if not exists
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    r, ext = os.path.splitext(dst)
                    if ext == '.tmpl':
                        with open(r, 'w') as f:
                            tmpl = env.get_template(relfn)
                            f.write(tmpl.render(**ctx))
                    else:
                        shutil.copyfile(src, dst)

                    print('created: {}'.format(dst))

    def run(self, args):
        path = os.path.join(os.getcwd(), args.project)
        args.project = os.path.basename(path)
        return self._gen_project(
                    path, skip=self._build_skip_files(args),
                    ctx=vars(args))


def main():
    root = argparse.ArgumentParser('sea')
    subparsers = root.add_subparsers()
    for k, v in globals().items():
        if k.endswith('Cmd') and issubclass(v, AbstractCommand):
            cmd = v()
            cmd.opt(subparsers).set_defaults(handler=cmd.run)

    args = sys.argv[1:]
    args = root.parse_args(args)
    args.handler(args)


def jobmain():
    rootp = argparse.ArgumentParser('seak')
    subparsers = rootp.add_subparsers()
    app = create_app(os.getcwd())
    import pkg_resources
    for ep in pkg_resources.iter_entry_points('sea.jobs'):
        ep.load()
    jobsroot = os.path.join(app.root_path, 'jobs')
    for m in os.listdir(jobsroot):
        if m.endswith('.py') and os.path.isfile(os.path.join(jobsroot, m)):
            import_string('jobs.{}'.format(m[:-3]))

    for name, handler in jobm.jobs.items():
        job = handler.job
        opts = getattr(handler, 'opts', [])
        p = subparsers.add_parser(name, *job.args, **job.kwargs)
        for opt in opts:
            p.add_argument(*opt.args, **opt.kwargs)
        p.set_defaults(handler=handler)

    args = sys.argv[1:]
    kwargs = vars(rootp.parse_args(args))
    handler = kwargs.pop('handler')
    handler(**kwargs)
