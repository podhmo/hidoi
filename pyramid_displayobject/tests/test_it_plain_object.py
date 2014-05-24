# -*- coding:utf-8 -*-
def _getTarget():
    from pyramid_displayobject import DisplayObjectFactory
    return DisplayObjectFactory


def _makeOne(iterator_factory):
    from pyramid_displayobject import (
        FieldFactory,
        WidgetManagement,
    )
    return _getTarget()(iterator_factory, FieldFactory(WidgetManagement()))


class Item(object):
    def __init__(self, name, value, created_at=None):
        self.name = name
        self.value = value
        self.created_at = created_at


def item_iterator(request, item, schema):
    from pyramid_displayobject.displayobject import required_of
    from pyramid_displayobject.displayobject import optional_of
    yield required_of(item, "name")
    yield required_of(item, "value")
    yield optional_of(item, "created_at")


def test_it():
    from pyramid_displayobject.displayobject import (
        DisplayObject,
        Field
    )
    target = _makeOne(item_iterator)

    request = None
    item0 = Item("Portion", "heal damage")

    dob = target(request, item0)

    assert isinstance(dob, DisplayObject)
    assert sorted(dob._fieldnames) == ["created_at", "name", "value"]

    assert isinstance(dob.name, Field)
    assert isinstance(dob.value, Field)
    assert isinstance(dob.created_at, Field)

    assert dob.name.value == "Portion"
    assert dob.value.value == "heal damage"
    assert dob.created_at.value is None

    assert dob.name.required is True
    assert dob.name.required is True
    assert dob.created_at.required is False
