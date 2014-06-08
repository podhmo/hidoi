# -*- coding:utf-8 -*-
def _getTarget():
    from hidoi.displayobject import DisplayObjectFactory
    return DisplayObjectFactory


def _makeOne(iterator_factory):
    from hidoi.displayobject import FieldFactory
    from hidoi.widget import WidgetManagement
    return _getTarget()(iterator_factory(FieldFactory(WidgetManagement(["text"]))))


class Item(object):
    def __init__(self, name, value, created_at=None):
        self.name = name
        self.value = value
        self.created_at = created_at


def item_itarator_factory(wm):
    def item_iterator(request, item, schema, name=""):
        from hidoi.displayobject import required_of
        from hidoi.displayobject import optional_of
        yield required_of(item, "name")
        yield required_of(item, "value")
        yield optional_of(item, "created_at")
    return item_iterator


def test_it():
    from hidoi.displayobject import (
        DisplayObject,
        Field
    )
    target = _makeOne(item_itarator_factory)

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
    assert dob.created_at._value is None
    assert dob.created_at.value is ""

    assert dob.name.required is True
    assert dob.name.required is True
    assert dob.created_at.required is False
