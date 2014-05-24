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
)


def includeme(config):
    config.include(".dynamicinterface")
    config.include(".displayobject")
