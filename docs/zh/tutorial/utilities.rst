utilities
==========

sea 提供了许多实用的函数和数据类型


sea.utils.import_string
^^^^^^^^^^^^^^^^^^^^^^^^
根据字符串路径导入模块 如 ``import_string()``

sea.utils.cached_property
^^^^^^^^^^^^^^^^^^^^^^^^^^^
属性缓存装饰器，可以将函数/方法的执行结果缓存至实例的属性字典中

sea.utils.Singleton
^^^^^^^^^^^^^^^^^^^^
元类，使用此元类的类都将变为单例

sea.datatypes.ImmutableDict
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

不可变字典，字典数据在初始化后不能改变，此类型可哈希
有如下两种方式去构造这个实例::

    # 1
    data = {'foo': 1, 'bar': 2, 'baz': 3}
    d = datatypes.ImmutableDict(data)

    # 2
    dd = datatypes.ImmutableDict.fromkeys(data.keys(), 'OK')

sea.datatypes.ConstantsObject
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

继承自 ``ImmutableDict`` 通过重写了 ``__getattr__`` 方法来使得可以通过属性访问 (`.`) 的方式访问字典内的数据
