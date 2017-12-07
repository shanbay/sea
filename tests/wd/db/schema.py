from orator.migrations import Migration


class InitDb(Migration):

    def up(self):
        with self.schema.create('users') as table:
            table.increments('id')
            table.string('username' 255)
            table.integer('age').unsigned().default(1)
            table.timestamp('created_at')
            table.timestamp('updated_at')
            table.big_integer('husband_id').nullable()
            table.big_integer('father_id').nullable()
            table.primary(['id'])

    def down(self):
        self.schema.drop('users')
