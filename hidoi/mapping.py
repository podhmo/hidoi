# -*- coding:utf-8 -*-
from alchemyjsonschema.mapping import (
    Mapping,
)
from jsonschema import FormatChecker
from alchemyjsonschema.dictify import ModelLookup
from jsonschema.validators import Draft4Validator
from zope.interface import implementer
from .interfaces import (
    IModelModule,
    IMapping,
)
from .langhelpers import model_of
from .schema import (
    get_schema,
    get_schema_convertion
)

Mapping = implementer(IMapping)(Mapping)


def get_mapping(request, model, name="name", validator=Draft4Validator, format_checker=FormatChecker()):
    model_module = request.registry.getUtility(IModelModule)
    reg = get_schema_convertion(request)
    schema = get_schema(request, model, name)
    modellookup = ModelLookup(model_module)
    return Mapping(validator(schema, format_checker=format_checker), model_of(model), modellookup, registry=reg)


def includeme(config):
    pass
