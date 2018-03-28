# 内置信号

sea 支持信号(基于 [blinker](https://github.com/jek/blinker))，并内置了一些信号(`blinker.Signal`)，位于 `sea.signals` 中

### `before_rpc`

rpc调用前触发，Sender 为 `None`，无额外参数。例如：

```python
from sea.signals import before_rpc

def handler(sender):
    assert sender is None

before_rpc.connect(handler)
```

### `after_rpc`

rpc调用后触发，Sender 为 `None`，无额外参数。

**注意**当 rpc 调用发生未处理的异常，该信号不会触发。

### `server_started`

grpc server 启动前触发，Sender 为 `sea.server.Server`对象，无额外参数。

### `server_stopped`

grpc server 结束后触发，Sender 为 `sea.server.Server`对象，无额外参数。
