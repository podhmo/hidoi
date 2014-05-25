# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi.api import get_schema_convertion
    return get_schema_convertion(*args, **kwargs)


class InvalidCall(Exception):
    pass


def jsonify_invalid_call(val):
    raise InvalidCall(val)


def normalize_invalid_call(val):
    raise InvalidCall(val)


def test_it0():
    from hidoi.testing import testConfigSlakky
    from hidoi.schema import DefaultRegistry
    with testConfigSlakky() as config:
        # configuration phase
        config.commit()

        # runtime phase
        request = config

        result = _callFUT(request)

        # value is eaual
        assert result.jsonify == DefaultRegistry.jsonify
        assert result.normalize == DefaultRegistry.normalize

        # but id is not same
        assert id(result.jsonify) != id(DefaultRegistry.jsonify)


def test_it__swapping_jsonify():
    from hidoi.testing import testConfigSlakky
    from hidoi.schema import DefaultRegistry
    with testConfigSlakky() as config:
        # configuration phase
        config.add_schema_convertion("date-time", jsonify=jsonify_invalid_call, normalize=None)
        config.commit()

        # runtime phase
        request = config

        result = _callFUT(request)
        assert result.jsonify[("string", "date-time")] == jsonify_invalid_call
        assert result.normalize[("string", "date-time")] == DefaultRegistry.normalize[("string", "date-time")]


def test_it__swapping_normalize():
    from hidoi.testing import testConfigSlakky
    from hidoi.schema import DefaultRegistry
    with testConfigSlakky() as config:
        # configuration phase
        config.add_schema_convertion("date-time", normalize=normalize_invalid_call, jsonify=None)
        config.commit()

        # runtime phase
        request = config

        result = _callFUT(request)
        assert result.normalize[("string", "date-time")] == normalize_invalid_call
        assert result.jsonify[("string", "date-time")] == DefaultRegistry.jsonify[("string", "date-time")]
