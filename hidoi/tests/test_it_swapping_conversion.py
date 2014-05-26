# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi.api import get_schema_convertion
    return get_schema_convertion(*args, **kwargs)


def jsonify_invalid_call(val):
    pass


def normalize_invalid_call(val):
    pass


def restriction_invalid_call(column, type):
    raise Exception("invalid")


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
        assert result.restriction == DefaultRegistry.restriction
        assert result.column_to_schema == DefaultRegistry.column_to_schema

        # but id is not same
        assert id(result.jsonify) != id(DefaultRegistry.jsonify)
        assert id(result.normalize) != id(DefaultRegistry.normalize)
        assert id(result.restriction) != id(DefaultRegistry.restriction)
        assert id(result.column_to_schema) != id(DefaultRegistry.column_to_schema)


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


def test_it_swapping_to_schema():
    import sqlalchemy.types as t
    from hidoi.testing import testConfigSlakky
    from hidoi.schema import DefaultRegistry
    with testConfigSlakky() as config:
        # configuration phase
        config.add_sqla_column_convertion(t.Integer, to_schema="*secret*")
        config.commit()

        # runtime phase
        request = config

        result = _callFUT(request)
        assert result.column_to_schema[t.Integer] == "*secret*"
        assert result.restriction[t.DateTime] == DefaultRegistry.restriction[t.DateTime]


def test_it_swapping_restriction():
    import sqlalchemy.types as t
    from hidoi.testing import testConfigSlakky
    import pytest

    with testConfigSlakky() as config:
        # configuration phase
        config.add_sqla_column_convertion(t.DateTime, restriction=restriction_invalid_call)
        config.commit()

        # runtime phase
        request = config

        result = _callFUT(request)

        with pytest.raises(Exception):
            for fn in result.restriction[t.DateTime]:
                fn(None, None)
