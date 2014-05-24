# -*- coding:utf-8 -*-
from pyramid.interfaces import IDict
from zope.interface import Interface


class ISchema(IDict):
    """ schema object, currently,  i expected jsonschema as member.
    """


class ISchemaFactory(Interface):
    def __call__(src, includes=None, excludes=None, overrides=None, depth=None):
        pass


class IDisplayObjectFactory(Interface):
    def __call__(model, schema):
        pass
