import sys
import os
import argparse
from orator.commands.application import application
import sea
from sea.cli import AbstractCommand


def _get_app():
    app = sea.current_app()
    if app is None:
        return sea.create_app(os.getcwd())
    return app


def get_dbconfig():
    app = _get_app()
    dbconfig = os.path.join(
        app.root_path, 'configs/{}/orator.py'.format(app.env))
    if not os.path.exists(dbconfig):
        dbconfig = os.path.join(
            app.root_path, 'configs/default/orator.py')
    return dbconfig


def parsed(args, names):
    rv = []
    for n in names:
        rv += ['--{}'.format(n.replace('_', '-')), getattr(args, n)]
    return rv


class CmdHelp(AbstractCommand):
    def opt(self, subparsers):
        return subparsers.add_parser(
            'help', help='Displays help for a command')

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'help'] + extra
        return application.run()


class CmdList(AbstractCommand):
    def opt(self, subparsers):
        return subparsers.add_parser(
            'list', help='Lists commands')

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'list'] + extra
        return application.run()


class CmdMigrate(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'migrate', help='Run the database migrations')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        p.add_argument(
            '--seed-path',
            default=os.path.join(root_path, 'db/seeds'),
            help='The path of migrations files to be executed')
        self.parmas = ['conf', 'path', 'seed_path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'migrate'] + parsed(args, self.parmas) + extra
        return application.run()


class CmdDbSeed(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'db:seed', help='Seed the database with records')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/seeds'),
            help='The path to seeders files.')
        self.parmas = ['conf', 'path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'db:seed'] + parsed(args, self.parmas) + extra
        return application.run()


class CmdMakeMigration(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'make:migration', help='Create a new migration file')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        self.parmas = ['path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'make:migration'] + \
            parsed(args, self.parmas) + extra
        return application.run()


class CmdMakeSeed(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'make:seed', help='Create a new seeder file')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/seeds'),
            help='The path to seeders files')
        self.parmas = ['path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'make:seed'] + parsed(args, self.parmas) + extra
        return application.run()


class CmdMigrateRest(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'migrate:reset', help='Rollback all database migrations')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        self.parmas = ['conf', 'path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'migrate:reset'] + \
            parsed(args, self.parmas) + extra
        return application.run()


class CmdMigrateRollback(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'migrate:rollback', help='Rollback the last database migration')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        self.parmas = ['conf', 'path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'migrate:rollback'] + \
            parsed(args, self.parmas) + extra
        return application.run()


class CmdMigrateStatus(AbstractCommand):
    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            'migrate:status', help='Show a list of migrations up/down')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        self.parmas = ['conf', 'path']
        return p

    def run(self, args, extra=[]):
        sys.argv = ['orator', 'migrate:status'] + \
            parsed(args, self.parmas) + extra
        return application.run()


def main():
    root = argparse.ArgumentParser('seaorator')
    subparsers = root.add_subparsers()
    for k, v in globals().items():
        if k.startswith('Cmd') and issubclass(v, AbstractCommand):
            cmd = v()
            cmd.opt(subparsers).set_defaults(handler=cmd.run)
    args = sys.argv[1:]
    args, extra = root.parse_known_args(args)
    args.handler(args, extra)
