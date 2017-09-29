command
=================

在完成安装后你的系统会增加这四个命令 ``sea`` 、 ``seak`` 、 ``seaorator`` 、 ``seacelery``。

sea 命令
^^^^^^^^

* ``sea server``: 运行 server 参数， ``--host`` 指定 publish host
* ``sea console``: 进入包含 ``app`` 实例的 REPL
* ``sea generate``: 根据 proto 文件转译成 Python 代码， ``-I`` 指定 proto 文件的路径。例如 ``sea generate -I proto_dir filename``
* ``sea new``: 创建一个新的工程 如 ``sea new projectname`` 默认会生成最完整的工程模版，当然也可以通过以下参数来跳过
    * ``--skip-git``     不执行 git init
    * ``--skip-orator``  不添加 orator 相关模版代码
    * ``--skip-cache``   不添加 cache 相关模版代码
    * ``--skip-celery``  不添加 celery 相关模版代码
    * ``--skip-consul``  不添加 consul 相关模版代码
    * ``--skip-sentry``  不添加 sentry 相关模版代码

seak 命令
^^^^^^^^^



seaorator 命令
^^^^^^^^^^^^^^

此命令包含以下选项

* ``list`` 显示所有命令
* ``make:seed`` 生成模版 seed 文件，默认生成路径在 ``db/seeds`` 下，例如 ``seaorator make:seed seedname``
* ``db:seed`` 执行 seed 文件，将测试数据填充进数据库
* ``migrate``: 进行 migrate
* ``make:migration``: 创建 migration 模版，默认文件生成路径在 ``db/migration/`` 下，例如 ``seaorator make:migration migrationame``
* ``migrate:status``: 显示 migration 文件在数据库中的执行状态，你会得到下面这样的输出::

    +---------------------------+------+
    | Migration                 | Ran? |
    +---------------------------+------+
    | 2017_09_21_045904_init_db | Yes  |
    | 2017_09_28_061944_add_col | No   |
    +---------------------------+------+

* ``migrate:rollback``: migration 回滚
* ``migrate:reset``: 回滚所有 migration


seacelery 命令
^^^^^^^^^^^^^^^

和 ``celery`` 命令用法相同
