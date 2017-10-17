from orator.migrations import Migration


class InitDb(Migration):

    def up(self):
        with self.schema.create('migrations') as table:

            table.primary(['id'])

        with self.schema.create('sqlite_sequence') as table:

            table.primary(['id'])

        with self.schema.create('users') as table:

            table.primary(['id'])

    def down(self):
        self.schema.drop('migrations')
        self.schema.drop('sqlite_sequence')
        self.schema.drop('users')
