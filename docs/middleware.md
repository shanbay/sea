# 中间件

### 使用中间件

中间件的调用架构如下：

```
       |
      \/
|-------------|
| middleware 1|
|-------------|
       |
|-------------|
| middleware 2|
|-------------|
       |
|-------------|
| grpc service|
|-------------|
       |
|-------------|
| middleware 2|
|-------------|
       |
|-------------|
| middleware 1|
|-------------|
       |
      \/
```

在 config 中设置 `MIDDLEWARES`，即可以启用相应的中间件，注意middleware的顺序

```python
MIDDLEWARES = [
    'middleware 1',
    'middleware 2'
]
```

### 编写中间件

- 继承 `sea.middleware.BaseMiddleware`
- 实现相应的方法：
    - 需要在请求处理之前执行操作，实现: `before_handler(self, servicer, request, context)`
    - 需要在请求处理之后执行操作，实现: `after_handler(self, servicer, response)`
    - 需要在请求处理前后均执行操作，实现: `__call__(self, servicer, request, context)`

### 内置中间件

**RpcErrorMiddleware**

在代码抛出的 `exceptions.RpcException` 及其子类的异常，均会被该 middleware 捕获，并转换为 GRPC 的相应响应，
响应中的 code 和 details 为 RpcException 中的 code, details 属性

**ServiceLogMiddleware**

会logging所有的请求，logging 的 level为 `info`
