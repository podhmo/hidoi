# -*- coding:utf-8 -*-
from .displayobject import (
    DisplayObjectFactory,
    FieldFactory,
    WidgetManagement,
    get_display,
    display_config
)
from .schema import (
    SingleModelSchemaFactory,
    AlsoChildrenSchemaFactory,
    OneModelOnlySchemaFactory,
    get_schema
)
from .widget import (
    get_widget_renderer
)

def includeme(config):
    config.include(".dynamicinterface")

    config.include(".schema")
    config.include(".widget")

    config.include(".displayobject")

    config.include(".verify")
