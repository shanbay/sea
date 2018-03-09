from app.extensions import pwx
import peewee


class User(pwx.Model):

    name = peewee.CharField()
