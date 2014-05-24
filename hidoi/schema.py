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
from .langhelpers import model_of


class SchemaTreatException(Exception):
    pass


def edit(schema, k, val):
    if k not in schema:
        raise SchemaTreatException("{} is not found in schema(edit)".format(k))
    schema[k] = val


def default(schema, k, val):
    if k in schema:
        return
    schema[k] = val


def new(schema, k, val):
    if k in schema:
        raise SchemaTreatException("{} is found in schema(create)".format(k))
    schema[k] = val


def get(schema, k, val):
    if k not in schema:
        raise SchemaTreatException("{} is not found in schema(get)".format(k))
    return schema[k]


def revive(schema, ks, name="required"):
    properties = get(schema, "properties")
    required = get(schema, name)
    for k in ks:
        if k not in properties:
            raise SchemaTreatException("{} is not participants of schema(revive)".format(k))
        required.append(k)


def reorder(schema, priorities, name="required"):
    """required=[a, b, c] , priorities={a: 2, c:-10} => ((-10, c), (0, b), (2, a)) => [c, b, a]"""
    required = get(schema, name)
    candidates = [(priorities.get(e, 0), e) for e in required]
    new_required = [e for _, e in sorted(candidates, key=lambda xs: xs[0])]
    edit(schema, name, new_required)


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

SingleModelSchemaFactory = CachedSchemaFactory(SchemaFactory(SingleModelWalker))
AlsoChildrenSchemaFactory = CachedSchemaFactory(SchemaFactory(AlsoChildrenWalker))
OneModelOnlySchemaFactory = CachedSchemaFactory(SchemaFactory(OneModelOnlyWalker))


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
