import copy
from sea.local import Proxy


def test_std_class_attributes():
    assert Proxy.__name__ == "Proxy"
    assert Proxy.__module__ == "sea.local"
    assert Proxy.__qualname__ == "sea.local"
    assert isinstance(Proxy.__doc__, str)


def test_name():
    def real():
        """real function"""
        return "REAL"

    x = Proxy(lambda: real)
    assert x.__name__ == "real"

    assert x.__doc__ == "real function"

    assert x.__class__ == type(real)
    assert x.__dict__ == real.__dict__
    assert repr(x) == repr(real)
    assert x.__module__


def test_local_proxy_operations_list():
    foo = []
    ls = Proxy(lambda: foo)
    ls.append(42)
    ls.append(23)
    ls[1:] = [1, 2, 3]
    assert foo == [42, 1, 2, 3]
    assert repr(foo) == repr(ls)
    assert foo[0] == 42
    foo += [1]
    assert list(foo) == [42, 1, 2, 3, 1]
    del ls[0]
    assert list(foo) == [1, 2, 3, 1]
    assert len(ls) == 4
    assert list(iter(ls)) == [1, 2, 3, 1]
    assert 1 in ls


def test_local_proxy_operations_math():
    foo = 2
    ls = Proxy(lambda: foo)
    assert ls + 1 == 3
    assert 1 + ls == 3
    assert ls - 1 == 1
    assert 1 - ls == -1
    assert ls * 1 == 2
    assert 1 * ls == 2
    assert ls / 1 == 2
    assert 1.0 / ls == 0.5
    assert ls // 1.0 == 2.0
    assert 1.0 // ls == 0.0
    assert ls % 2 == 0
    assert 2 % ls == 0
    assert 2 == foo
    assert ls == 2
    assert ls != 1
    assert ls > 1
    assert ls >= 1
    assert ls < 4
    assert ls <= 4
    assert divmod(ls, 1) == (2, 0)
    assert divmod(4, ls) == (2, 0)
    assert ls ** 2 == 4
    assert ls >> 2 == 0
    assert ls << 10 == 2048
    assert ls ^ 3 == 1
    assert ls & 3 == 2
    assert ls | 5 == 7
    assert -ls == -foo
    assert +ls == +foo
    assert abs(ls) == abs(foo)
    assert ~ls == ~foo
    assert complex(ls) == complex(foo)
    assert float(ls) == float(foo)
    assert int(ls) == int(foo)
    assert oct(ls) == oct(foo)
    assert hex(ls) == hex(foo)


def test_local_proxy_operations_boolean():
    foo = object()
    ls = Proxy(lambda: foo)
    assert ls and True
    assert not (ls and False)
    assert (ls or False) == foo


def test_hash():
    foo = 2
    ls = Proxy(lambda: foo)
    assert hash(ls) == hash(foo)


def test_call():
    l = lambda x: x
    ls = Proxy(lambda: l)
    assert ls(2) == l(2)


def test_dir():
    foo = 2
    ls = Proxy(lambda: foo)
    assert dir(ls) == dir(foo)
    assert ls.__members__ == dir(foo)


def test_set_get_del():
    class A:
        def __init__(self):
            self.b = 1

    a = A()
    ls = Proxy(lambda: a)
    delattr(ls, "b")
    assert not hasattr(ls, "b")
    assert not hasattr(a, "b")
    a.x = 2
    assert hasattr(a, "x")


def test_local_proxy_operations_strings():
    foo = "foo"
    ls = Proxy(lambda: foo)
    assert str(ls) == "foo"
    assert ls + "bar" == "foobar"
    assert "bar" + ls == "barfoo"
    assert ls * 2 == "foofoo"

    foo = "foo %s"
    assert ls % ("bar",) == "foo bar"


def test_local_proxies_with_callables():
    foo = 42
    ls = Proxy(lambda: foo)
    assert ls == 42
    foo = [23]
    ls.append(42)
    assert ls == [23, 42]
    assert foo == [23, 42]


def test_deepcopy_on_proxy():
    class Foo(object):
        attr = 42

        def __copy__(self):
            return self

        def __deepcopy__(self, memo):
            return self

    f = Foo()
    p = Proxy(lambda: f)
    assert p.attr == 42
    assert copy.deepcopy(p) is f
    assert copy.copy(p) is f

    a = []
    p2 = Proxy(lambda: [a])
    assert copy.copy(p2) == [a]
    assert copy.copy(p2)[0] is a

    assert copy.deepcopy(p2) == [a]
    assert copy.deepcopy(p2)[0] is not a
