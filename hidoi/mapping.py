# -*- coding:utf-8 -*-
from alchemyjsonschema.mapping import (
    Mapping,
    DefaultRegistry
)
from alchemyjsonschema.dictify import ModelLookup
from jsonschema.validators import Draft4Validator
from zope.interface import implementer
from .interfaces import (
    IModelModule,
    IMapping,
    ISchemaConvertionRegistry
)
from .langhelpers import model_of
from .schema import get_schema

Mapping = implementer(IMapping)(Mapping)
DefaultRegistry = implementer(ISchemaConvertionRegistry)(DefaultRegistry)


@implementer(ISchemaConvertionRegistry)
class MyConversionRegistry(object):
    def __init__(self):
        self.jsonify = DefaultRegistry.jsonify.copy()
        self.normalize = DefaultRegistry.normalize.copy()


def get_schema_convertion(request):
    return request.registry.queryUtility(ISchemaConvertionRegistry) or DefaultRegistry


def get_mapping(request, model, name="name", validator=Draft4Validator):
    model_module = request.registry.getUtility(IModelModule)
    reg = get_schema_convertion(request)
    schema = get_schema(request, model, name)
    modellookup = ModelLookup(model_module)
    return Mapping(validator(schema), model_of(model), modellookup, registry=reg)


def add_schema_conversion(config, format_name, jsonify, normalize, type_name="string"):
    def closure():
        reg = config.registry.getUtility(ISchemaConvertionRegistry)
        k = (type_name, format_name)
        if jsonify is not None:
            reg.jsonify[k] = jsonify
        if normalize is not None:
            reg.normalize[k] = normalize
    config.action(None, closure)


def includeme(config):
    config.registry.registerUtility(MyConversionRegistry(), ISchemaConvertionRegistry)
    config.add_directive("add_schema_conversion", add_schema_conversion)
