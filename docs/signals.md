# 内置信号

sea 支持信号(基于 [blinker](https://github.com/jek/blinker))，并内置了一些信号(`blinker.Signal`)，位于 `sea.signals` 中

### `server_started`

grpc server 启动前触发，Sender 为 `sea.server.Server`对象，无额外参数。

### `server_stopped`

grpc server 结束后触发，Sender 为 `sea.server.Server`对象，无额外参数。


### `post_ready`

sea app ready 后触发，Sender 为 `sea.app.BaseApp`的子类对象，无额外参数。
