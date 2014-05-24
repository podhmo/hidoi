# -*- coding:utf-8 -*-
class Item(object):
    def __init__(self, name, value, created_at=None):
        self.name = name
        self.value = value
        self.created_at = created_at

from pyramid_displayobject.displayobject import required_of


def item_iterator(request, item, schema):
    yield required_of(item, "name")
    yield required_of(item, "value")

from pyramid_displayobject import (
    DisplayObjectFactory,
    FieldFactory,
    WidgetManagement,
)

factory = DisplayObjectFactory(item_iterator, FieldFactory(WidgetManagement()))

item0 = Item("Portion", "heal damage")
dob0 = factory(None, item0)


print(dob0)
print(dob0.name)
print(dob0.value)
