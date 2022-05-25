# 工具类和函数

## `import_string`

尝试根据字符串内容去 import 模块或者对象

```python
from sea import utils

utils.import_string('datetime.date')
utils.import_string('sea.app:BaseApp')
```

## `cached_property`

> 如果你使用的是 python 3.8 以上版本，标准库中已经提供 cached_property 装饰器，推荐使用官方版本
> `from functools import cached_property`

property 的值初次计算后会缓存在 instance 上，重复调用不会重复计算

```python
class ForTest:

    def __init__(self):
        self.count = 0

    @utils.cached_property
    def cached_count(self):
        return self.count

ins = ForTest()
assert ins.cached_count == 0
ins.count = 10
assert ins.cached_count == 0
```

## `Singleton`

单实例类

```python
class A(metaclass=utils.Singleton):
    pass

s1 = A()
s2 = A()
assert s1 is s2
```
