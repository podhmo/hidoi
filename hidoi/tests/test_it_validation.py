# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi.api import get_validation
    return get_validation(*args, **kwargs)


def increment_validation(wrapper, data, *args, **kwargs):
    data.value += 1
    return data


def increment_validation2(wrapper, data, *args, **kwargs):
    data.value += 10
    return data


class Data(object):  # for name_of
    def __init__(self, v):
        self.value = v


def test_it__call_with_another_name__missing():
    from hidoi.testing import testConfigSlakky
    with testConfigSlakky() as config:
        # configuration phase
        config.add_validation(Data, increment_validation, name="create")
        config.commit()

        # runtime phase
        request = config

        wrapper = None
        data = Data(0)

        assert data.value == 0
        result = _callFUT(request, data)
        result(wrapper, data)
        assert data.value == 0


def test_it__multiple__different__call_twice():
    from hidoi.testing import testConfigSlakky
    with testConfigSlakky() as config:
        # configuration phase
        config.add_validation(Data, increment_validation, name="create")
        config.add_validation(Data, increment_validation2, name="create")
        config.commit()

        # runtime phase
        request = config

        wrapper = None
        data = Data(0)

        assert data.value == 0
        result = _callFUT(request, data, name="create")
        result(wrapper, data)
        assert data.value == 11


def test_it__multiple__same__call_once():
    from hidoi.testing import testConfigSlakky
    with testConfigSlakky() as config:
        # configuration phase
        config.add_validation(Data, increment_validation, name="create")
        config.add_validation(Data, increment_validation, name="create")
        config.add_validation(Data, increment_validation, name="create")
        config.add_validation(Data, increment_validation, name="create")
        config.commit()

        # runtime phase
        request = config

        wrapper = None
        data = Data(0)

        assert data.value == 0
        result = _callFUT(request, data, name="create")
        result(wrapper, data)
        assert data.value == 1

