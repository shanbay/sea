import sys
import os
import argparse
import abc
import pkg_resources

from sea import create_app
from sea.server import Server
from sea.utils import import_string


class JobException(RuntimeError):
    pass


class JobOption:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class JobManager:

    def __init__(self):
        self._jobs = {}

    def job(self, name, *args, **kwargs):
        def wrapper(func):
            func.job = JobOption(*args, **kwargs)
            self._jobs[name] = func
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

    @property
    def jobs(self):
        return self._jobs


jobm = JobManager()


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
        app = create_app(os.getcwd())
        s = Server(app, args.host)
        s.run()
        return 0


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
        ctx = {'app': create_app(os.getcwd())}
        try:
            from IPython import embed
            h, kwargs = embed, dict(banner1=banner, user_ns=ctx)
        except ImportError:
            import code
            h, kwargs = code.interact, dict(banner=banner, local=ctx)
        h(**kwargs)
        return 0


class GenerateCmd(AbstractCommand):
    def opt(self, subparsers):
        p = subparsers.add_parser(
            'generate', aliases=['g'], help='Generate')
        p.add_argument(
            '-I', '--proto_path', required=True, default=os.getcwd(),
            help="the dir in which we'll search the proto files")
        p.add_argument(
            'protos', nargs='+',
            help='the proto files which will be compiled.'
            'the paths are related to the path defined in "-I"')
        return p

    def run(self, args):
        from grpc_tools import protoc
        proto_out = os.path.join(create_app(os.getcwd()).root_path, 'protos')
        cmd = [
            'grpc_tools.protoc',
            '--proto_path', args.proto_path,
            '--python_out', proto_out,
            '--grpc_python_out', proto_out
        ] + [os.path.join(args.proto_path, f) for f in args.protos]
        return protoc.main(cmd)


class NewCmd(AbstractCommand):

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
        'sentry': [],
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
        p.add_argument(
            '--skip-sentry', action='store_true', help='skip sentry')
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
        self._gen_project(
                path, skip=self._build_skip_files(args),
                ctx=vars(args))
        return 0


def main():
    root = argparse.ArgumentParser('sea')
    subparsers = root.add_subparsers()
    for k, v in globals().items():
        if k.endswith('Cmd') and issubclass(v, AbstractCommand):
            cmd = v()
            cmd.opt(subparsers).set_defaults(handler=cmd.run)

    args = sys.argv[1:]
    if len(args) > 0:
        args = root.parse_args(args)
        return args.handler(args)
    root.print_help()


def jobmain():
    rootp = argparse.ArgumentParser('seak')
    subparsers = rootp.add_subparsers()
    app = create_app(os.getcwd())
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
    try:
        handler(**kwargs)
        return 0
    except JobException as e:
        return e
