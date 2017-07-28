from sea.register import ConsulRegister

from tests.helpers import MockConsulClient


def test_consul_register():

    register = ConsulRegister(MockConsulClient())
    assert register.register('greeter', '1024')
    assert register.get_port('greeter') == '1024'
    assert register.deregister('greeter')
    assert register.get_port('greeter') is None
