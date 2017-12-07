import json
from sea.format import msg2dict, stream2dict, msg2json, dict2msg
from tests.wd.protos import helloworld_pb2
from tests.wd.protos import sample_pb2

def test_msg2dict(app):
    request = helloworld_pb2.HelloRequest(name="value")
    ret = msg2dict(request)
    assert ret == {"name": "value"}

    pb = sample_pb2.MessageOfTypes()
    pb.i32 = 666
    pb.flot = 3.14
    pb.bol = True
    pb.nested.req = "hahahaa"
    pb.str_repeated.append("dhueife")
    pb.str_repeated.append("fhrvrjvnj")

    pb.simpleMap['s1'] = 3.1415
    pb.simpleMap['s2'] = 4.1235
    res = msg2dict(pb)
    assert res['bol'] == True
    assert res['flot'] == 3.14
    assert res['nested'] == {"req": "hahahaa"}
    assert res["str_repeated"] == ["dhueife", "fhrvrjvnj"]
    assert res["simpleMap"]['s1'] == 3.1415

    # test including_default_value_fields
    res = msg2dict(pb, including_default_value_fields=True)
    assert res['i64'] == 0
    assert res['strng'] == ""

    # test user_enum_label
    pb.enm = 2
    res = msg2dict(pb)
    assert res['enm'] == 2
    res = msg2dict(pb, use_enum_labels=True)
    assert res['enm'] == "C"

    # test keys
    res = msg2dict(pb, keys=['bol', 'flot'])
    assert res == {"bol": True, "flot": 3.14}


def test_msg2json():
    pb = sample_pb2.MessageOfTypes()
    pb.i32 = 666
    pb.flot = 3.14
    pb.bol = True
    pb.nested.req = "hahahaa"
    pb.str_repeated.append("dhueife")
    pb.str_repeated.append("fhrvrjvnj")

    pb.simpleMap['s1'] = 3.1415
    pb.simpleMap['s2'] = 4.1235
    res_json = msg2json(pb)
    res = json.loads(res_json)
    assert res['flot'] == 3.14
    assert res['nested'] == {"req": "hahahaa"}
    assert res["str_repeated"] == ["dhueife", "fhrvrjvnj"]
    assert res["simpleMap"]['s1'] == 3.1415


def test_dict2msg():
    d = {'flot': 3.14, 'i32': 666, 'bol': True, 'nested': {'req': 'hahahaa'},
         'enm': 2, 'str_repeated': ['dhueife', 'fhrvrjvnj'],
         'simpleMap': {'s1': 3.1415, 's2': 4.1235}}
    res_msg = dict2msg(d, sample_pb2.MessageOfTypes())
    res = msg2dict(res_msg)
    for k, v in d.items():
        assert res[k] == v


def test_stream2dict():
    def stream_generator():
        for i in range(5):
            yield helloworld_pb2.HelloRequest(name=str(i))

    ret = stream2dict(stream_generator())
    for i, part in enumerate(ret):
        assert part == {"name": str(i)}