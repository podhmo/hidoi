# -*- coding:utf-8 -*-
from .displayobject import (
    DisplayObjectFactory,
    FieldFactory,
    WidgetManagement,
    get_display
)
from .schema import (
    SingleModelSchemaFactory,
    AlsoChildrenSchemaFactory,
    OneModelOnlySchemaFactory,
    get_schema
)


def includeme(config):
    config.include(".dynamicinterface")
    config.include(".schema")
    config.include(".displayobject")
