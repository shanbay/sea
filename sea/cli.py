import sys
import os
import argparse
import pkg_resources

from sea import create_app
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

    def job(self, name, inapp=True, proxy=False, *args, **kwargs):
        def wrapper(func):
            func.parser = JobOption(*args, **kwargs)
            func.inapp = inapp
            func.proxy = proxy
            self._jobs[name] = func
            return func
        return wrapper

    def option(self, *args, **kwargs):
        def wrapper(func):
            opts = getattr(func, 'opts', [])
            opts.append(JobOption(*args, **kwargs))
            func.opts = opts
            return func
        return wrapper

    @property
    def jobs(self):
        return self._jobs


jobm = JobManager()


def main():
    root = argparse.ArgumentParser('sea')
    subparsers = root.add_subparsers()

    path = os.getcwd()
    sys.path.append(path)

    # load builtin
    import_string('sea.cmds')

    # load lib jobs
    for ep in pkg_resources.iter_entry_points('sea.jobs'):
        ep.load()

    # load app jobs
    try:
        import_string('jobs')
    except ImportError:
        pass
    else:
        appjobs = os.path.join(path, 'jobs')
        for m in os.listdir(appjobs):
            if m != '__init__.py' and m.endswith('.py'):
                import_string('jobs.{}'.format(m[:-3]))

    # build parser
    for name, handler in jobm.jobs.items():
        parser = handler.parser
        opts = getattr(handler, 'opts', [])
        p = subparsers.add_parser(name, *parser.args, **parser.kwargs)
        for opt in opts:
            p.add_argument(*opt.args, **opt.kwargs)
        p.set_defaults(handler=handler)

    args = sys.argv[1:]
    known, argv = root.parse_known_args(args)
    kwargs = vars(known)
    handler = kwargs.pop('handler')
    try:
        if handler.inapp:
            create_app(path)
        if handler.proxy:
            handler(**kwargs, argv=argv)
        else:
            handler(**kwargs)
        return 0
    except JobException as e:
        return e
