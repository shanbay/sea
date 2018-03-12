# 项目结构

## 约定优于配置

你并不是唯一美丽的雪花。如果能放弃那些毫无意义的个人喜好，你就可以跳出诸多无谓选择的牢笼，在那些真正重要的领域快速前进。

有谁会在乎你的数据库主键采用什么格式吗？选择 id，postId，posts_id 或 pid 真的那么重要吗？这真的值得反复讨论才做出决定吗？当然不。

约定优于配置，不仅可以让我们避免许多无谓的思考，而且为更深层的抽象提供了肥沃的土壤。优良约定的威力就在于：每个广泛使用它们的领域都会受益颇丰。

`Sea` 正是遵循“约定优于配置”

## 项目目录结构

每个 `Sea` 项目都有固定的目录结构，特定的功能实现置于特定的 module 中。下面是一个最基本的 `Sea` 项目的目录结构

```
.
├── app
│   ├── extensions.py
│   ├── __init__.py
│   └── servicers.py
├── configs
│   ├── default
│   │   ├── __init__.py
│   ├── development
│   │   └── __init__.py
│   ├── __init__.py
│   └── testing
│       └── __init__.py
├── jobs
│   └── __init__.py
├── protos
├── requirements.txt
└── tests
    └── __init__.py
```

### app

`app` 目录中包含项目的主体代码，其中最核心的是 `__init__.py`, `extensions.py`, `servicers.py`

> `__init__.py`:

定义了一个继承自 `sea.app.BaseApp` 的类： `App`

可以通过覆盖父类的方法，覆盖 `App` 的行为，也可以通过实现 `hook` 方法，定制初始化过程，例如定义 `ready` 方法，该方法会在`App` 初始化完成后执行。

关于 `sea.app.BaseApp` 的详细接口，请参见文档：[App](app)

> `extensions.py`:

声明了项目需要的 "扩展"，`sea` 支持通过 "扩展" 的方式来集成第三方的库，例如 orm, cache 等等。
每个扩展往往包括一个“扩展类”和需要的相应的配置，在 `extensions.py`中实力化这个“扩展类”，并在项目中设置好这些配置，就可以使用了。

以内置的 `cache` 扩展为例：


```python
# extensions.py
from sea.contrib.extensions.cache import Cache
cache = Cache()
```

使用方法一：

```python
from sea import current_app
current_app.extensions.cache
```

使用方法二：

```python
from app.extensions import cache
```

关于 extension 的更多内容，请参见文档：[扩展](extension)

> `servicers.py`:

定义了 GRPC 的 Servicer，继承自根据 proto 文件生成的同名 Servicer 类，并以 `sea.servicer.ServicerMeta` 为 metaclass。例如：

```python
from sea.servicer import ServicerMeta
class GreeterServicer(greeter_pb2_grpc.GreeterServicer, metaclass=ServicerMeta):
    def SayHello(self, request, context):
        return greeter_pb2.Message(msg='Hello')
```

### configs

根据不同的使用环境(例如: development, testing, production)分组存放的配置文件，实际执行的时候，会根据 `SEA_ENV` 的值加载同名的配置。

配置均为正常的 `py` 文件。

主要配置，请参见文档：[项目配置](configuration)

### jobs

包含项目的自定义命令，关于命令的定义和调用方法，以及内置命令等，请参考文档：[命令系统](cmdline)

### protos

根据 proto 文件生成的 `py` 文件，一般一个 proto 文件会生产两个 `py` 文件。

### tests

包含项目的相关测试。关于如何编写和运行测试，请参考文档：[测试](testing)
