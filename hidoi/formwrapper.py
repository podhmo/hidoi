# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

import venusian
from alchemyjsonschema.dictify import ErrorFound  # this is used. not delete.
from .interfaces import IValidation
from .dynamicinterface import make_interface_from_class
from .langhelpers import (
    model_of,
    funcname,
    RepeatableSetQueue
)
from .mapping import get_mapping
from .displayobject import get_display


def get_validation(request, model, name=""):
    isrc = make_interface_from_class(model)
    validations = request.registry.adapters.lookup([isrc], IValidation, name)

    def execute(wrapper, data, something):
        model_cls_name = model_of(model).__name__
        if validations is None:
            logger.info("*validation(%s): validation is not found. model=%s", name, model_cls_name)
            return data
        for v in validations:
            logger.debug("*validation(%s): function=%s. model=%s", name, v, model_cls_name)
            data = v(wrapper, data, something)
        return data
    return execute


def add_validation(config, model, fn, name="", order=0):
    model = config.maybe_dotted(model)
    fn = config.maybe_dotted(fn)
    config.inspect_model_action(model, name, order, ("validation", funcname(fn)))  # traceability

    adapters = config.registry.adapters
    isrc = make_interface_from_class(model_of(model))
    validations = adapters.lookup([isrc], IValidation, name)
    if validations is None:
        queue = RepeatableSetQueue("{}:{}".format(model_of(model).__name__, name))
        queue.add(fn, order=order)
        adapters.register([isrc], IValidation, name, queue)
    else:
        validations.add(fn, order=order)


def validation_config(model, name="", order=0):
    def _validation_config(fn):
        def callback(context, funcname, ob):
            config = context.config.with_package(info.module)
            config.add_validation(model, fn, name=name, order=order)
        info = venusian.attach(fn, callback, category='hidoi.validation')
        return fn
    return _validation_config


class FormWrapper(object):
    def __init__(self, request, model, name="",
                 get_mapping=get_mapping,
                 get_validation=get_validation,
                 get_display=get_display):
        self.request = request
        self.mapping = get_mapping(request, model, name)
        self.model = model
        self.name = name
        self.rawdata = None

        self.get_validation = get_validation
        self.get_display = get_display

    def validate(self, data, something=None):
        self.rawdata = data
        self.mapping.validate_all_jsondict(data)
        data = self.mapping.dict_from_jsondict(data)
        validation = self.get_validation(self.request, self.model, self.name)
        if validation is None:
            logger.info("validation is not found model=%s, name=%s", self.model, self.name)
            return data
        return validation(self, data, something)

    def to_displayobject(self):
        return self.get_display(self.request, self.model, self.name)


class Something(dict):
    __getattr__ = dict.__getitem__


def includeme(config):
    config.add_directive("add_validation", add_validation)
