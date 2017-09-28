from orator.migrations import Migration


class InitDb(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.big_increments('id')
            table.string('username')
            table.integer('age').unsigned().default(1)
            table.timestamps()
            table.big_integer('husband_id').nullable()
            table.big_integer('father_id').nullable()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
