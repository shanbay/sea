from sea.cli import taskm


@taskm.task('assign')
@taskm.option('-n', '--name', default='Hello')
def f1(name):
    return name


@taskm.task('plusone')
@taskm.option('-n', '--number', type=int)
def f2(number):
    return number + 1
