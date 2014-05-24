# -*- coding:utf-8 -*-
class Item(object):
    def __init__(self, name, value, created_at=None):
        self.name = name
        self.value = value
        self.created_at = created_at

    schema = {"type": "object",
              "properties": {"name": {"type": "string", "widget": "text"},
                             "value": {"type": "string", "widget": "text", "description": "effect of item"},
                             "created_at": {"type": "date-time", "widget": "date-time"}},
              "required": ["name", "value"]}


def required_of(ob, name, format="text"):
    return name, getattr(ob, name), format, True, {}


def optional_of(ob, name, format="text"):
    return name, getattr(ob, name), format, False, {}


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
dob0 = factory(None, item0, None)


print(dob0)
print(dob0.name)
print(dob0.value)
