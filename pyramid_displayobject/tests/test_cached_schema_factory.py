# -*- coding:utf-8 -*-
def _getTarget():
    from pyramid_displayobject.schema import CachedSchemaFactory
    return CachedSchemaFactory


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


class OnceOnlyCallSchema(object):
    def __init__(self, schema):
        self.life = 1
        self.schema = schema

    def __call__(self, *args, **kwargs):
        if self.life <= 0:
            raise Exception
        self.life -= 1
        return self.schema


def test_it():
    expected = object()
    target = _makeOne(OnceOnlyCallSchema(expected))

    result = target(object(), includes=["id", "name"], overrides={"id": "1"}, depth=1)
    assert result == expected


def test_prepare():
    import pytest
    expected = object()
    target = OnceOnlyCallSchema(expected)

    target(object(), includes=["id", "name"], overrides={"id": "1"}, depth=1)
    with pytest.raises(Exception):
        target(object(), includes=["id", "name"], overrides={"id": "1"}, depth=1)


def test_it__cache():
    expected = object()
    model = object()
    target = _makeOne(OnceOnlyCallSchema(expected))

    result = target(model, includes=["id", "name"], overrides={"id": "1"}, depth=1)
    result = target(model, includes=["id", "name"], overrides={"id": "1"}, depth=1)
    result = target(model, includes=["id", "name"], overrides={"id": "1"}, depth=1)
    result = target(model, includes=["id", "name"], overrides={"id": "1"}, depth=1)
    result = target(model, includes=["id", "name"], overrides={"id": "1"}, depth=1)
    assert result == expected
