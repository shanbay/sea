from orator.orm import has_one, has_many, belongs_to
from sea.contrib.extensions.orator import Model, cache_model


class User(Model, metaclass=cache_model.ModelMeta):

    __fillable__ = ('username', 'age')

    @belongs_to
    def husband(self):
        return User

    @has_one('husband_id')
    def wife(self):
        return User

    @belongs_to
    def father(self):
        return User

    @has_many('father_id')
    def children(self):
        return User
