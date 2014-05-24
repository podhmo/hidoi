# -*- coding:utf-8 -*-
from .displayobject import (
    DisplayObjectFactory,
    FieldFactory,
    WidgetManagement
)
from .schema import (
    SingleModelSchemaFactory,
    AlsoChildrenSchemaFactory,
    OneModelOnlySchemaFactory,
    schema_iterator
)


def includeme(config):
    config.include(".dynamicinterface")
    config.include(".displayobject")
