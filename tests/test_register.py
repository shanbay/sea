from sea.register import ConsulRegister

from tests.helpers import MockConsulClient


def test_consul_register():

    register = ConsulRegister(MockConsulClient())
    assert register.register('greeter', '127.0.0.1', 1024)
    assert register.service_url('greeter') == 'greeter.service.consul:1024'
    assert register.deregister('greeter')
    assert register.service_url('greeter') is None
