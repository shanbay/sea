# 数据结构

sea 提供些内置的可能会对大家有用的数据结构


## `ImmutableDict` 不可变的字典

一旦初始化成功，不再可以进行字典的变更操作

**实例化**

```python
import datatypes
import copy

data = {'foo': 1, 'bar': 2, 'baz': 3}

# 实例化
d1 = datatypes.ImmutableDict(data)
assert sorted(d1.keys()) == ['bar', 'baz', 'foo']
assert d1['foo'] == 1

d2 = d1.copy()
assert d2['foo'] == 1
assert type(d2) == dict

d3 = copy.copy(d1)
assert d2['foo'] == 1
assert type(d3) == datatypes.ImmutableDict

d4 = datatypes.ImmutableDict.fromkeys(data.keys(), 'OK')
assert sorted(d4.keys()) == ['bar', 'baz', 'foo']
assert d4['foo'] == 'OK'
assert type(d4) == datatypes.ImmutableDict
```

**操作**

```python
d1.clear()
>> raise TypeError

d1.pop('bar')
>> raise TypeError

d['a'] = 1
>> raise TypeError
```

## `ConstantsObject` 不可变object

根据dict初始化对象，dict的 key value 会被转化为object的 attribute。初始化成功后不可以再更改 attribute

```python
data = {'foo': 1, 'bar': 2, 'baz': 3}
d = datatypes.ConstantsObject(data)
assert d.foo == 1

d.foo = 2
>> raise TypeError
```
