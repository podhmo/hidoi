# -*- coding:utf-8 -*-
from zope.interface import implementer
from alchemyjsonschema import (
    SchemaFactory,
    AlsoChildrenWalker,
    SingleModelWalker,
    OneModelOnlyWalker
)
from .interfaces import (
    ISchema,
    ISchemaFactory
)
from .dynamicinterface import make_interface_from_class


def edit(schema, k, val):
    if k not in schema:
        raise KeyError("{} is not found in schema".format(k))
    schema[k] = val


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
            v = self.cache[k] = self.schema_factory(src)
            return v

SingleModelSchemaFactory = CachedSchemaFactory(SchemaFactory(SingleModelWalker))
AlsoChildrenSchemaFactory = CachedSchemaFactory(SchemaFactory(AlsoChildrenWalker))
OneModelOnlySchemaFactory = CachedSchemaFactory(SchemaFactory(OneModelOnlyWalker))


def get_schema(request, model, name=""):
    iface = make_interface_from_class(model.__class__)
    adapters = request.registry.adapters
    return adapters.lookup([iface], ISchema, name)


def add_schema(config, model, schema, name=""):
    isrc = config.dynamic_interface(model)
    register = config.registry.adapters.register
    register([isrc], ISchema, name, schema)
    return schema


def includeme(config):
    config.add_directive("add_schema", add_schema)
