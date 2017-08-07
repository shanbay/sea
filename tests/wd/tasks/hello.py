from sea.cli import taskm
from sea import current_app


@taskm.task('getconfig')
@taskm.option('-n', '--name', default='TESTING')
def f1(name):
    app = current_app()
    return app.config.get(name)


@taskm.task('plusone')
@taskm.option('-n', '--number', type=int)
def f2(number):
    return number + 1
