servicer
=================


servicer 和 gRPC 的 servicer 用法基本一致::

    import helloworld_pb2
    import helloworld_pb2_grpc

    from sea.servicer import ServicerMeta


    class HelloServicer(helloworld_pb2_grpc.HelloServicer, metaclass=ServicerMeta):

        # your code

不过还是有一些区别的，你需要使用 ``sea.servicer.ServicerMeta`` 这个元类，他会为你 servicer 的每个方法都包裹上中间件。另外，需要注意的是这里可以直接 ``import helloworld_pb2`` 而这个模块是位于 protos 目录下。这是因为 sea 在初始化时会执行::

    sys.path.append(root_path)
    sys.path.append(os.path.join(root_path, 'protos'))


`sea.servicer` 还提供了 `msg2dict` `stream2dict` 两个工具函数来帮助你方便的将 msg 转换成 dict::

    def msg2dict(msg, keys=None):
      if keys is not None:
          return {k: getattr(msg, k) for k in keys}

      return {k.name: v
              for k, v in msg.ListFields()}


    def stream2dict(stream):
        yield from map(msg2dict, stream)
