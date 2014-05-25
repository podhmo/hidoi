# -*- coding:utf-8 -*-
from zope.interface import implementer
from pyramid.exceptions import ConfigurationError
from alchemyjsonschema import (
    SchemaFactory,
    AlsoChildrenWalker,
    Classifier
)
from alchemyjsonschema.mapping import (
    DefaultRegistry
)
from .interfaces import (
    ISchema,
    ISchemaFactory,
    ISchemaConvertionRegistry
)
from .dynamicinterface import make_interface_from_class
from .langhelpers import model_of


@implementer(ISchemaFactory)
class CachedSchemaFactory(object):
    def __init__(self, schema_factory):
        self.schema_factory = schema_factory
        self.cache = {}

    def for_cache(self, x):
        if x is None:
            return None
        elif isinstance(x, (tuple, list)):
            return tuple(x)
        elif hasattr(x, "items"):
            return tuple(x.items())
        else:
            return x

    def __call__(self, src, includes=None, excludes=None, overrides=None, depth=None):
        k_includes = self.for_cache(includes)
        k_excludes = self.for_cache(excludes)
        k_overrides = self.for_cache(overrides)
        k_depth = self.for_cache(depth)
        k = tuple([src, k_includes, k_excludes, k_overrides, k_depth])
        try:
            return self.cache[k]
        except KeyError:
            v = self.cache[k] = self.schema_factory(src, includes=includes, excludes=excludes, overrides=overrides, depth=depth)
            return v


DefaultRegistry = implementer(ISchemaConvertionRegistry)(DefaultRegistry)


@implementer(ISchemaConvertionRegistry)
class MyConversionRegistry(object):
    def __init__(self):
        self.jsonify = DefaultRegistry.jsonify.copy()
        self.normalize = DefaultRegistry.normalize.copy()
        self.restriction = DefaultRegistry.restriction.copy()
        self.column_to_schema = DefaultRegistry.column_to_schema.copy()


def get_schema_convertion(request):
    return request.registry.queryUtility(ISchemaConvertionRegistry) or DefaultRegistry


def add_sqla_column_convertion(config, column_type, to_schema=None, restriction=None):
    def closure():
        reg = config.registry.getUtility(ISchemaConvertionRegistry)
        if to_schema is not None:
            reg.column_to_schema[column_type] = to_schema
        if restriction:
            reg.restriction[column_type] = restriction
    config.action(None, closure)


def add_schema_convertion(config, format_name, jsonify=None, normalize=None, type_name="string"):
    def closure():
        reg = config.registry.getUtility(ISchemaConvertionRegistry)
        k = (type_name, format_name)
        if jsonify is not None:
            reg.jsonify[k] = jsonify
        if normalize is not None:
            reg.normalize[k] = normalize
    config.action(None, closure)


def get_schema_factory(request, walker=AlsoChildrenWalker):
    isrc = make_interface_from_class(walker)
    adapters = request.registry.adapters
    schema_factory = adapters.lookup([isrc], ISchemaFactory)
    if schema_factory is None:
        sreg = get_schema_convertion(request)
        schema_factory = CachedSchemaFactory(SchemaFactory(walker, classifier=Classifier(sreg.column_to_schema)))
        adapters.register([isrc], ISchemaFactory, "", schema_factory)
    return schema_factory


def get_schema(request, model, name=""):
    iface = make_interface_from_class(model_of(model))
    adapters = request.registry.adapters
    return adapters.lookup([iface], ISchema, name)


def add_schema(config, model, schema, name=""):
    isrc = config.dynamic_interface(model)
    register = config.registry.adapters.register
    register([isrc], ISchema, name, schema)
    return schema


def includeme(config):
    config.add_directive("add_schema", add_schema)
    config.add_directive("add_schema_convertion", add_schema_convertion)
    config.add_directive("add_sqla_column_convertion", add_sqla_column_convertion)
    config.registry.registerUtility(MyConversionRegistry(), ISchemaConvertionRegistry)

