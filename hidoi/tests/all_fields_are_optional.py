# -*- coding:utf-8 -*-
from hidoi.displayobject import display_config
from hidoi.operate import edit
from .models import Item


@display_config(Item)
def modify_item_schema(request, item, schema):
    # all fields are optional fields
    edit(schema, "required", [])
    return schema
