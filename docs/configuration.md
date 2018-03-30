# 配置

## 配置的加载

配置由项目根目录下的 python 模块: `configs` 决定
`configs`根据运行环境分成若干子模块，默认包括： development, production, testing
程序运行的时候，会根据 `SEA_ENV` 环境变量的值加载同名的 `configs` 子模块

## 基本配置

`DEBUG`

> 是否开启 debug 模式，默认值：`False`

`TESTING`

> 是否为测试，默认值：`False`

`TIMEZONE`

> 时区，默认值：`'UTC'`

`GRPC_WORKERS`

> GRPC server 的 worker 数，默认值：`3`

`GRPC_HOST`

> GRPC server bind 的地址，默认值：`'[::]'`

`GRPC_PORT`

> GRPC server 的端口，默认值：`6000`

`GRPC_LOG_LEVEL`

> GRPC server logging 的 level，默认值：`'WARNING'`

`GRPC_LOG_HANDLER`

> GRPC server 的 logging handler，默认值：`logging.StreamHandler()`

`GRPC_LOG_FORMAT`

> GRPC server 的 logging format，默认值：`'[%(asctime)s %(levelname)s in %(module)s] %(message)s`

`GRPC_GRACE`

> GRPC server 的 grace 参数，默认值：`5`

`PROMETHEUS_SCRAPE`

> 是否打开相关服务供 prometheus 抓取 metrics，需要安装 [prometheus_client](https://github.com/prometheus/client_python)，默认值: `False`

`PROMETHEUS_PORT`

> 供 prometheus 抓取的服务的端口，默认值：`9091`

`MIDDLEWARES`

> 按照顺序为“由外到内”排列的 middleware，默认值：`['sea.middleware.RpcErrorMiddleware']`
