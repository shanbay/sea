import sys
import os
import argparse
from orator.commands.application import application
import sea


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


class BaseCmd:
    ORATOR_CMD = None
    ORATOR_OPT = []

    def parsed(self, args, names):
        rv = []
        for n in names:
            rv += ['--{}'.format(n.replace('_', '-')), getattr(args, n)]
        return rv

    def opt(self, subparsers):
        raise NotImplementedError

    def run(self, args, extra=[]):
        sys.argv = ['orator', self.ORATOR_CMD] + \
            self.parsed(args, self.ORATOR_OPT) + extra
        return application.run()


class CmdHelp(BaseCmd):
    ORATOR_CMD = 'help'

    def opt(self, subparsers):
        return subparsers.add_parser(
            self.ORATOR_CMD, help='Displays help for a command')


class CmdList(BaseCmd):
    ORATOR_CMD = 'list'

    def opt(self, subparsers):
        return subparsers.add_parser(
            self.ORATOR_CMD, help='Lists commands')


class CmdMigrate(BaseCmd):
    ORATOR_CMD = 'migrate'
    ORATOR_OPT = ['conf', 'path', 'seed_path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Run the database migrations')
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
        return p


class CmdDbSeed(BaseCmd):
    ORATOR_CMD = 'db:seed'
    ORATOR_OPT = ['conf', 'path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Seed the database with records')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/seeds'),
            help='The path to seeders files.')
        return p


class CmdMakeMigration(BaseCmd):
    ORATOR_CMD = 'make:migration'
    ORATOR_OPT = ['path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Create a new migration file')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        return p


class CmdMakeSeed(BaseCmd):
    ORATOR_CMD = 'make:seed'
    ORATOR_OPT = ['path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Create a new seeder file')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/seeds'),
            help='The path to seeders files')
        return p


class CmdMigrateRest(BaseCmd):
    ORATOR_CMD = 'migrate:reset'
    ORATOR_OPT = ['conf', 'path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Rollback all database migrations')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        return p


class CmdMigrateRollback(BaseCmd):
    ORATOR_CMD = 'migrate:rollback'
    ORATOR_OPT = ['conf', 'path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Rollback the last database migration')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        return p


class CmdMigrateStatus(BaseCmd):
    ORATOR_CMD = 'migrate:status'
    ORATOR_OPT = ['conf', 'path']

    def opt(self, subparsers):
        root_path = _get_app().root_path
        p = subparsers.add_parser(
            self.ORATOR_CMD, help='Show a list of migrations up/down')
        p.add_argument(
            '-c', '--conf', default=get_dbconfig(),
            help='The config file path')
        p.add_argument(
            '-p', '--path',
            default=os.path.join(root_path, 'db/migrations'),
            help='The path of migrations files to be executed')
        return p


def main():
    root = argparse.ArgumentParser('seaorator')
    subparsers = root.add_subparsers()
    for k, v in globals().items():
        if k.startswith('Cmd') and issubclass(v, BaseCmd):
            cmd = v()
            cmd.opt(subparsers).set_defaults(handler=cmd.run)
    args = sys.argv[1:]
    args, extra = root.parse_known_args(args)
    args.handler(args, extra)
