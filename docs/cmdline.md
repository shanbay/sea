# 命令系统

## 如何编写和运行命令

有时候为了执行一些操作，需要写一些命令，例如数据迁移。
为 sea 的项目编写命令是非常简单的。


例如要创建一个 `print` 命令，接受一个可选参数 '-d/--date'，默认值是 2017-11-11'， 一个位置参数 'content'

则可以在项目根目录下的 `jobs/__init__.py` 中加入以下代码

```python
from sea.cli import jobm

@jobm.job('print')
@jobm.option('-d', '--date', default='2017-11-11')
@jobm.option('content')
def f1(date, content):
    print(content, 'at', date)
    return 0
```

这时候在命令行中可以得到如下效果

```sh
$ sea print -d 2017-12-12 Hello
Hello at 2017-12-12
```

**关于 jobm的具体用法**

`@jobm.option(*args, **kwargs)`

`*args` 和 `**kwargs`: 同 [argparse.ArgumentParser.add_argument](https://docs.python.org/3/library/argparse.html#the-add-argument-method)

`@jobm.job(name, inapp=True, env='development', proxy=False, *args, **kwargs)`

`name`: 命令的名称，例如上例中的 name 为 'print'，可以在命令中通过 `sea print` 来执行

`inapp`: 是否需实例化一个 [app](app)，如果需要，该命令需要在项目根目录下执行，默认为`True`

`env`: `SEA_ENV` 环境变量的默认值

`proxy`: 是否为一个转发命令, 默认 `False`。所谓转发命令，就是执行函数会接收一个额外参数 `argv`，其值为命令中传入的 `@jobm.option` 中未定义的参数的列表。例如

```python
@jobm.job('print', proxy=True)
@jobm.option('-d', '--date', default='2017-11-11')
def f1(date, argv):
    print(*argv, 'at', date)
    return 0
```

则效果如下：
```
$ sea print Hello World
Hello World at 2017-11-11
```

`*args` 和 `**kwargs`: 同 [argparse.ArgumentParser](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser)


## 内置的命令

sea 内置一些命令，包括：

- `server`: 启动 grpc server，需要在 sea 项目目录中执行
- `console`: 运行一个　sea 项目的交互命令行，需要在 sea 项目目录中执行
- `generate`: 编译 proto 文件为对应的 py 文件，需要在 sea 项目目录中执行
- `test`: 运行项目测试，需要在 sea 项目目录中执行
- `async_task`: 启动执行异步任务的 celery worker，需要在 sea 项目目录中执行
- `bus`: 启动执行 bus 任务的 celery worker，需要在 sea 项目目录中执行
- `new`：新建 sea 项目，不需要在 sea 项目目录中执行

对应用法均可在命令后加上 `--help/-h` 参数查看

## 第三方库中的命令

如果第三方库需要提供命令，可以将相关命令加入到 setup.py 中的 setup 的 entry_points 的 `sea.jobs` 列表中。
例如你的第三方库叫 "sea_ext"，其中 `sea_ext.cmds` 中定义了如下命令：

```python
@jobm.job('sayhello')
def printf():
    print('Hello')
```

那么在 setup.py 中调用 setup 时加入如下参数：

```python
entry_points={
        'sea.jobs': [
            'sayhello=sea_ext.cmds:printf',
        ]
    }
```

则就可以通过 `sea sayhello` 调用相关命令了

## 项目中的命令

项目中的命令可以定义在 `jobs` 目录下的 `__init__.py`或者其他 `py` 文件中
