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
from .langhelpers import model_of, funcname, get_pairs_iterator


class UnSuppport(Exception):
    pass


@implementer(IDisplayObjectFactory)
class DisplayObjectFactory(object):
    def __init__(self, iterator_factory):
        self.iterator_factory = iterator_factory

    def __call__(self, request, ob, name="", schema=None, min_of_items=1):
        iterator = self.iterator_factory(request, ob, schema, name=name)
        return DisplayObject(request, iterator, ob, name=name, min_of_items=min_of_items)


@implementer(IDisplayObject)
class DisplayObject(object):
    def __init__(self, request, iterator, ob, name="", min_of_items=1):
        self.request = request
        self._usecase_name = name
        self.iterator = iterator
        self.ob = ob
        self._fieldnames = []
        for field in iterator:
            self._fieldnames.append(field.name)
            setattr(self, field.name, field)
        self.unknown_errors = []
        self.min_of_items = min_of_items

    def __repr__(self):
        return "<Disp:%s at 0x%x>" % (self.ob.__class__.__name__, id(self))

    def merge_errors(self, errors):
        for k, vs in get_pairs_iterator(errors):
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

    def _get_class_from_properties(self, field):
        # xxx: this is trikky workaround.
        from sqlalchemy.inspection import inspect
        return inspect(model_of(self.ob)).get_property(field.name).mapper.class_

    def child(self, field, min_of_items=None):
        if min_of_items is None:
            min_of_items = self.min_of_items

        if not field._value:  # None or ""
            if min_of_items <= 0:
                return None
            else:
                model_class = self._get_class_from_properties(field)
                return get_display(self.request, model_class, name=self._usecase_name, min_of_items=0)
        return get_display(self.request, field._value, name=self._usecase_name, min_of_items=0)

    def children(self, field, min_of_items=None):
        if min_of_items is None:
            min_of_items = self.min_of_items

        if len(field._value) > 0:
            return [get_display(self.request, e, name=self._usecase_name, min_of_items=0)
                    for e in field._value]
        elif min_of_items <= 0:
                return []
        else:
            model_class = self._get_class_from_properties(field)
            return [get_display(self.request, model_class, name=self._usecase_name, min_of_items=0)]


class FieldFactory(object):
    def __init__(self, widget_management, FieldClass=None):
        self.widget_management = widget_management
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
        attrs["_value"] = value
        attrs["ob"] = ob
        attrs["widget"] = widget
        attrs["required"] = required
        attrs["visible"] = visible
        attrs["errors"] = []

    def __repr__(self):
        fmt = ('Field[name={o.name!r}, value={o.value!r}, widget={o.widget!r}, '
               'required={o.required!r}, count_of_error={count_of_error}, kwargs={o.kwargs!r}]')
        return fmt.format(o=self, count_of_error=len(self.errors))

    @property
    def value(self):
        if self._value is None:
            return ""
        return self._value

    def __getattr__(self, name):
        return self.kwargs[name]

    def __setattr__(self, name, val):
        self.kwargs[name] = val


def required_of(ob, name, format="text"):
    return Field(name, ob, getattr(ob, name), format, True, True)


def optional_of(ob, name, format="text"):
    return Field(name, ob, getattr(ob, name), format, False, True)


class SchemaIteratorFactory(object):
    def __init__(self, field_factory):
        self.field_factory = field_factory

    def detect_widget(self, sub):
        try:
            if sub["type"] == "array":
                return "array"
            elif sub["type"] == "object":
                return "object"
            elif sub["type"] == "boolean":
                return "boolean"
            elif sub["type"] == "integer":
                return "number"
            elif sub["type"] == "number":
                return "number"
            else:
                return None
        except KeyError:
            return "object"

    def detect_subschema(self, sub, widget):
        if widget == "object":
            if "properties" in sub:
                return sub["properties"]
            else:
                return sub
        elif widget == "array":
            return sub["items"]
        else:
            return None

    def __call__(self, request, ob, schema, name=""):
        schema = schema or get_schema(request, ob, name=name)
        assert schema
        required = schema["required"]
        visible = schema.get("visible", required)

        use_default = model_of(ob) == ob

        for name, sub in schema["properties"].items():
            # individual
            widget = sub.get("widget")
            if widget is None:
                widget = self.detect_widget(sub) or "text"
            subschema = self.detect_subschema(sub, widget)

            kwargs = {"label": sub.get("description", name), "schema": subschema}
            value = "" if use_default else getattr(ob, name)
            yield self.field_factory(name, ob, value, widget, (name in required), (name in visible), **kwargs)


def get_display(request, ob, name="", min_of_items=1):
    adapters = request.registry.adapters
    isrc = make_interface_from_class(model_of(ob))
    factory = adapters.lookup([isrc], IDisplayObject, name)
    if factory is None:
        raise Exception("Not found display object. isrc=%s, name=%s", isrc, name)
    return factory(request, ob, name=name, min_of_items=min_of_items)


def add_display(
        config,
        model,
        modifier=None,
        name="",
        includes=None,
        excludes=None,
        overrides=None,
        depth=2,
        iterator_factory=SchemaIteratorFactory,
        walker=AlsoChildrenWalker):
    model = config.maybe_dotted(model)
    modifier = config.maybe_dotted(modifier)
    isrc = config.dynamic_interface(model)

    config.inspect_model_action(model, name, 0, ("modifier", funcname(modifier)))  # traceability
    _name = name
    if modifier is None:
        def get_display_object__no_modified(request, ob, name="", min_of_items=1):
            factory = request.registry.getUtility(IDisplayObjectFactory)
            assert name == _name
            return factory(request, ob, name=name, min_of_items=min_of_items)
        config.registry.adapters.register([isrc], IDisplayObject, name, get_display_object__no_modified)
    else:
        def create_display_object(request, ob, name="", min_of_items=1):
            assert name == _name
            schema = get_schema(request, ob, name=name)
            template = schema.copy()
            template["visible"] = template["required"].copy()
            modified = modifier(request, ob, template)
            if modifier is None:
                logger.warn("modifier return None: schema=%s", schema)
                modified = template

            factory = request.registry.getUtility(IDisplayObjectFactory)
            return factory(request, ob, schema=modified, name=name, min_of_items=min_of_items)
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
        depth=2,
        iterator_factory=SchemaIteratorFactory,
        walker=AlsoChildrenWalker):
    def _display_config(modifier):
        def callback(context, funcname, ob):
            config = context.config.with_package(info.module)
            config.add_display(model, modifier, name=name, includes=includes, excludes=excludes, overrides=overrides, depth=depth, iterator_factory=iterator_factory, walker=walker)
        info = venusian.attach(modifier, callback, category='hidoi.displayobject')
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
            default_factory = factory or DisplayObjectFactory(SchemaIteratorFactory(FieldFactory(widget_management)))
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
