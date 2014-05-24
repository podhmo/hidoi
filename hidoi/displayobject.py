# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import venusian
from .schema import (
    AlsoChildrenSchemaFactory,
    get_schema
)
from zope.interface import implementer
from .interfaces import (
    IDisplayObjectFactory,
    IDisplayObject
)
from .dynamicinterface import make_interface_from_class
from .langhelpers import model_of


class UnSuppport(Exception):
    pass


@implementer(IDisplayObjectFactory)
class DisplayObjectFactory(object):
    def __init__(self, iterator_factory, field_factory):
        self.iterator_factory = iterator_factory
        self.field_factory = field_factory

    def __call__(self, request, ob, name="", schema=None):
        iterator = self.iterator_factory(request, ob, schema, name=name)
        return DisplayObject(iterator, self.field_factory, ob)


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


def schema_iterator(request, ob, schema, name=""):
    schema = schema or get_schema(request, ob, name=name)
    assert schema
    required = schema["required"]
    for name, sub in schema["properties"].items():
        yield name, getattr(ob, name), sub.get("widget", "text"), (name in required), {"label": sub.get("description", name)}


def get_display(request, ob, name=""):
    adapters = request.registry.adapters
    isrc = make_interface_from_class(model_of(ob))
    factory = adapters.lookup([isrc], IDisplayObject, name)
    return factory(request, ob)


default_field_factory = FieldFactory(WidgetManagement())


def add_display(
        config,
        model,
        modifier=None,
        name="",
        includes=None,
        excludes=None,
        overrides=None,
        depth=None,
        field_factory=default_field_factory,
        schema_iterator=schema_iterator,
        schema_factory=AlsoChildrenSchemaFactory):
    model = config.maybe_dotted(model)
    modifier = config.maybe_dotted(modifier)
    schema = schema_factory(model, includes=includes, excludes=excludes, overrides=overrides, depth=depth)
    config.add_schema(model, schema, name=name)
    isrc = config.dynamic_interface(model)
    if modifier is None:
        def get_display_object__no_modified(request, ob):
            factory = request.registry.getUtility(IDisplayObjectFactory)
            return factory(request, ob, name=name)
        config.registry.adapters.register([isrc], IDisplayObject, name, get_display_object__no_modified)
    else:
        def create_display_object(request, ob):
            schema = get_schema(request, ob, name=name)
            template = schema.copy()

            modified = modifier(request, ob, template)
            if modifier is None:
                logger.warn("modifier return None: schema=%s", schema)
                modified = template

            factory = request.registry.getUtility(IDisplayObjectFactory)
            return factory(request, ob, schema=modified, name=name)
        config.registry.adapters.register([isrc], IDisplayObject, name, create_display_object)


def display_config(
        model,
        name="",
        includes=None,
        excludes=None,
        overrides=None,
        depth=None,
        field_factory=default_field_factory,
        schema_iterator=schema_iterator,
        schema_factory=AlsoChildrenSchemaFactory):
    def _display_config(modifier):
        def callback(context, funcname, ob):
            config = context.config.with_package(info.module)
            config.add_display(model, modifier, name=name, includes=includes, excludes=excludes, overrides=overrides, depth=depth, field_factory=field_factory, schema_iterator=schema_iterator, schema_factory=schema_factory)
        info = venusian.attach(modifier, callback, category='displayobject')
        return modifier
    return _display_config


def includeme(config):
    config.include(".schema")
    config.add_directive("add_display", add_display)
    default_factory = DisplayObjectFactory(schema_iterator, FieldFactory(WidgetManagement()))
    config.registry.registerUtility(default_factory, IDisplayObjectFactory)
