from sea.cli import jobm
from sea import current_app


@jobm.job('getconfig')
@jobm.option('-n', '--name', default='TESTING')
def f1(name):
    app = current_app()
    return app.config.get(name)


@jobm.job('plusone')
@jobm.option('-n', '--number', type=int)
def f2(number):
    return number + 1
