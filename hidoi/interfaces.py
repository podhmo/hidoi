# -*- coding:utf-8 -*-
from pyramid.interfaces import IDict
from zope.interface import (
    Interface,
    Attribute
)


class IModelModule(Interface):
    """ model modules. (i.e. <application>.models)
    """


class ISchema(IDict):
    """ schema object, currently,  i expected jsonschema as member.
    """


class IDisplayObject(Interface):
    """ display objecs has some attributes. a attrubute is almost Field class object.
    """
    def __iter__():
        pass


class IField(Interface):
    name = Attribute("name")
    value = Attribute("value")
    widget = Attribute("widget string")
    errors = Attribute("errors list")
    required = Attribute("using or not when ")


class IMapping(Interface):
    def jsondict_from_object(ob):
        """jsonify"""

    def dict_from_jsondict(jsondict):
        """normalize"""

    def dict_from_object(ob):
        """dictify"""

    def object_from_dict(params, strict=True):
        """objectify"""

    def validate_all_jsondict(jsondict):
        """validate all fields"""


class ISchemaFactory(Interface):
    def __call__(src, includes=None, excludes=None, overrides=None, depth=None):
        pass


class IDisplayObjectFactory(Interface):
    def __call__(model, schema):
        pass


class IWidgetManagement(Interface):
    def is_correct(widget):
        pass


class IWidgetRenderer(Interface):
    def render(**kwargs):
        pass
