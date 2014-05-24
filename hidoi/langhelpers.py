# -*- coding:utf-8 -*-
from sqlalchemy.ext.declarative.api import DeclarativeMeta


def model_of(object_or_class):
    if isinstance(object_or_class, DeclarativeMeta):
        return object_or_class  # class
    else:
        return object_or_class.__class__  # object
