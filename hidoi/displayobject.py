# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import venusian
from alchemyjsonschema import AlsoChildrenWalker
from .schema import (
    get_schema,
    get_schema_factory
)
from zope.interface import implementer
from .interfaces import (
    IDisplayObjectFactory,
    IDisplayObject,
    IField,
    IWidgetManagement
)
from .dynamicinterface import make_interface_from_class
from .langhelpers import model_of
from .widget import WidgetManagement


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


@implementer(IDisplayObject)
class DisplayObject(object):
    def __init__(self, iterator, field_factory, ob):
        self.iterator = iterator
        self.ob = ob
        self.field_factory = field_factory
        self._fieldnames = []
        for name, value, widget, required, visible, kwargs in iterator:
            field = field_factory(name, ob, value, widget, required, visible, **kwargs)
            self._fieldnames.append(name)
            setattr(self, name, field)
        self.unknown_errors = []

    def __repr__(self):
        return "<Disp:%s at 0x%x>" % (self.ob.__class__.__name__, id(self))

    def merge_errors(self, errors):
        for k, vs in errors:
            field = getattr(self, k, None)
            if field is None:
                err = self.unknown_errors
            else:
                err = field.errors
            for v in vs:
                err.append(v)

    def __iter__(self):
        for name in self._fieldnames:
            yield getattr(self, name)


class FieldFactory(object):
    def __init__(self, widget_management, reserved=["name", "widget"], FieldClass=None):
        self.widget_management = widget_management
        self.reserved = reserved[:]  # hmm.
        self.FieldClass = FieldClass or Field

    def __call__(self, name, ob, val, widget, required, visible, **kwargs):
        if not self.widget_management.is_correct(widget):
            raise UnSuppport("widget {}".format(widget))
        return self.FieldClass(name, ob, val, widget, required=required, visible=visible, **kwargs)


@implementer(IField)
class Field(object):
    def __init__(self, name, ob, value, widget, required=True, visible=True, **kwargs):
        attrs = self.__dict__
        attrs["kwargs"] = kwargs
        attrs["name"] = name
        attrs["value"] = value
        attrs["ob"] = ob
        attrs["widget"] = widget
        attrs["required"] = required
        attrs["visible"] = visible
        attrs["errors"] = []

    def __repr__(self):
        fmt = ('Field[name={o.name!r}, value={o.value!r}, widget={o.widget!r}, '
               'required={o.required!r}, count_of_error={count_of_error}, kwargs={o.kwargs!r}]')
        return fmt.format(o=self, count_of_error=len(self.errors))

    def __getattr__(self, name):
        return self.kwargs[name]

    def __setattr__(self, name, val):
        self.kwargs[name] = val


def required_of(ob, name, format="text"):
    return name, getattr(ob, name), format, True, True, {}


def optional_of(ob, name, format="text"):
    return name, getattr(ob, name), format, False, True, {}


def schema_iterator(request, ob, schema, name=""):
    schema = schema or get_schema(request, ob, name=name)
    assert schema
    required = schema["required"]
    visible = schema.get("visible", required)
    for name, sub in schema["properties"].items():
        yield name, getattr(ob, name), sub.get("widget", "text"), (name in required), (name in visible), {"label": sub.get("description", name)}


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
        walker=AlsoChildrenWalker):
    model = config.maybe_dotted(model)
    modifier = config.maybe_dotted(modifier)
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
            template["visible"] = template["required"].copy()
            modified = modifier(request, ob, template)
            if modifier is None:
                logger.warn("modifier return None: schema=%s", schema)
                modified = template

            factory = request.registry.getUtility(IDisplayObjectFactory)
            return factory(request, ob, schema=modified, name=name)
        config.registry.adapters.register([isrc], IDisplayObject, name, create_display_object)

    def closure():
        schema_factory = get_schema_factory(config, walker)
        schema = schema_factory(model, includes=includes, excludes=excludes, overrides=overrides, depth=depth)
        config.add_schema(model, schema, name=name)
    config.action(None, closure)


def display_config(
        model,
        name="",
        includes=None,
        excludes=None,
        overrides=None,
        depth=None,
        field_factory=default_field_factory,
        schema_iterator=schema_iterator,
        walker=AlsoChildrenWalker):
    def _display_config(modifier):
        def callback(context, funcname, ob):
            config = context.config.with_package(info.module)
            config.add_display(model, modifier, name=name, includes=includes, excludes=excludes, overrides=overrides, depth=depth, field_factory=field_factory, schema_iterator=schema_iterator, walker=walker)
        info = venusian.attach(modifier, callback, category='displayobject')
        return modifier
    return _display_config


def set_display_object_factory(config, factory=None):
    def closure():
        if factory is not None:
            default_factory = factory
        else:
            widget_management = config.registry.queryUtility(IWidgetManagement)
            if widget_management is None:
                return
            default_factory = factory or DisplayObjectFactory(schema_iterator, FieldFactory(widget_management))
        config.registry.registerUtility(default_factory, IDisplayObjectFactory)

    if factory is None:
        from pyramid.interfaces import PHASE2_CONFIG
        order = PHASE2_CONFIG
    else:
        order = None
    config.action(None, closure, order=order)


def includeme(config):
    config.include(".schema")
    config.include(".widget")
    config.add_directive("add_display", add_display)
    config.add_directive("set_display_object_factory", set_display_object_factory)
    # it's is not good, but...
    config.set_display_object_factory()
