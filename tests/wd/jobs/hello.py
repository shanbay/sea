from sea.cli import jobm, JobException
from sea import current_app


@jobm.job("config_hello")
@jobm.option("-n", "--name", default="ATTR")
def f1(name):
    raise JobException(name)


@jobm.job("plusone")
@jobm.option("-n", "--number", type=int)
def f2(number):
    app = current_app
    app.config["NUMBER"] = number + 1
