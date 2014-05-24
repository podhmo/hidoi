# -*- coding:utf-8 -*-
from pyramid_displayobject import display_config
from pyramid_displayobject.schema import edit
from .models import Item


@display_config(Item)
def modify_item_schema(request, item, schema):
    # all fields are optional fields
    edit(schema, "required", [])
    return schema
