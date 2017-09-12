
import grpc
from google.protobuf.json_format import SerializeToJsonError
from sea.utils import import_string, protobuf2dict


class _Call:
    def __init__(self, app, stub, fun_name):
        self.app = app
        self.stub = stub
        self.fun_name = fun_name

    def __call__(self, *args, **kwargs):
        func = getattr(self.stub, self.fun_name)
        kwargs['timeout'] = self.app.config.get('TIMEOUT') or 2
        try:
            res = func(*args, **kwargs)
            res_dict = protobuf2dict(res)
        except grpc.RpcError as e:
            return None, repr(e)
        except SerializeToJsonError as e:
            return None, repr(e)
        except Exception as e:
            return None, repr(e)
        else:
            return res_dict, None


class Client:
    """
    sea client implements

    example:
    from helloworld_pb2_grpc import GreeterStub
    helloworld_client = Client(app, 'helloworld', GreeterStub)
    res, err = client.SayHello(helloworld_pb2.HelloRequest(name='you'))
    """

    def __init__(self, app, service_name, stub_class):
        self.app = app
        regconf = self.app.config.get_namespace('REGISTER_')
        regclass = import_string(regconf['class'])
        self.register = regclass(
            self.app.extensions[regconf['client']])

        self.target_url = self.register.service_url(
            service_name) or "localhost:6000"

        self.channel = grpc.insecure_channel(self.target_url)
        self.stub = stub_class(self.channel)

    def __getattr__(self, func_name):
        return _Call(self.app, self.stub, func_name)


