# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from .schema import (
    AlsoChildrenSchemaFactory,
    get_schema
)
from zope.interface import implementer
from .interfaces import IDisplayObjectFactory


class UnSuppport(Exception):
    pass


@implementer(IDisplayObjectFactory)
class DisplayObjectFactory(object):
    def __init__(self, iterator_factory, field_factory):
        self.iterator_factory = iterator_factory
        self.field_factory = field_factory

    def __call__(self, request, ob, schema, name=""):
        iterator = self.iterator_factory(request, ob, schema)
        return DisplayObject(iterator, self.field_factory, ob, name=name)


class DisplayObject(object):
    def __init__(self, iterator, field_factory, ob):
        self.iterator = iterator
        self.ob = ob
        self.field_factory = field_factory
        self._fieldnames = []
        for name, value, widget, required, kwargs in iterator:
            field = field_factory(name, ob, value, widget, required, **kwargs)
            self._fieldnames.append(name)
            setattr(self, name, field)

    def __repr__(self):
        return "<Disp:%s at 0x%x>" % (self.ob.__class__.__name__, id(self))

default_widgets = ["text", "date-time"]  # xxx


class WidgetManagement(object):
    def __init__(self, defaults=default_widgets):
        self.formats = set(default_widgets[:])

    def is_correct(self, widget):
        return widget in self.formats

    def add(self, widget):
        self.formats.add(widget)


class FieldFactory(object):
    def __init__(self, widget_management, reserved=["name", "widget"], FieldClass=None):
        self.widget_management = widget_management
        self.reserved = reserved[:]  # hmm.
        self.FieldClass = FieldClass or Field

    def __call__(self, name, ob, val, widget, required, **kwargs):
        if not self.widget_management.is_correct(widget):
            raise UnSuppport("widget {}".format(widget))
        return self.FieldClass(name, ob, val, widget, required=required, **kwargs)


class Field(object):
    def __init__(self, name, ob, value, widget, required=True, **kwargs):
        attrs = self.__dict__
        attrs["kwargs"] = kwargs
        attrs["name"] = name
        attrs["value"] = value
        attrs["ob"] = ob
        attrs["widget"] = widget
        attrs["required"] = required

    def __repr__(self):
        fmt = ('Field[name={o.name!r}, value={o.value!r}, widget={o.widget!r}, '
               'required={o.required!r}, kwargs={o.kwargs!r}]')
        return fmt.format(o=self)

    def __getattr__(self, name):
        return self.kwargs[name]

    def __setattr__(self, name, val):
        self.kwargs[name] = val


def required_of(ob, name, format="text"):
    return name, getattr(ob, name), format, True, {}


def optional_of(ob, name, format="text"):
    return name, getattr(ob, name), format, False, {}


def schema_iterator(request, ob, schema):
    required = schema["required"]
    for name, sub in schema["properties"].items():
        yield name, getattr(ob, name), sub.get("widget", "text"), (name in required), {"label": sub.get("description", name)}


def add_display(
        config,
        model,
        modifier,
        name="",
        includes=None,
        excludes=None,
        overrides=None,
        depth=None,
        field_factory=FieldFactory(WidgetManagement()),
        schema_iterator=schema_iterator,
        schema_factory=AlsoChildrenSchemaFactory):
    model = config.maybe_dotted(model)
    modifier = config.maybe_dotted(modifier)
    schema = schema_factory(model, includes=includes, excludes=excludes, overrides=overrides, depth=depth)
    config.add_schema(model, schema, name=name)

    def create_display_object(request, ob):
        schema = get_schema(request, ob)
        template = schema.copy()

        modified = modifier(request, template)
        if modifier is None:
            logger.warn("modifier return None: schema=%s", schema)
            modified = template

        factory_factory = request.getUtility(IDisplayObjectFactory)
        return factory_factory(request, ob, modified)


def includeme(config):
    config.include(".schema")
    default_factory = DisplayObjectFactory(schema_iterator, FieldFactory(WidgetManagement()))
    config.registerUtility(default_factory, IDisplayObjectFactory)
