# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import re
from zope.interface import (
    implementer,
    provider,
)
from collections import defaultdict

import venusian
from alchemyjsonschema.dictify import (
    ErrorFound,
    ConvertionError
)
from pyramid.decorator import reify

from .interfaces import (
    IValidation,
    IExceptionHandler,
    IHandlerLookup
)
from .dynamicinterface import make_interface_from_class
from .langhelpers import (
    model_of,
    funcname,
    RepeatableSetQueue
)
from .mapping import get_mapping
from .displayobject import get_display


class ValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors


def get_validation(request, model, name=""):
    isrc = make_interface_from_class(model_of(model))
    validations = request.registry.adapters.lookup([isrc], IValidation, name)

    def execute(wrapper, data, something=None):
        model_cls_name = model_of(model).__name__
        if validations is None:
            logger.info("*validation(%s): validation is not found. model=%s", name, model_cls_name)
            return data

        error_raised = False
        for v in validations:
            try:
                logger.debug("*validation(%s): function=%s. model=%s", name, v, model_cls_name)
                data = v(wrapper, data, something)
            except Exception as e:
                error_raised = True
                handler = wrapper.handler_lookup(e)
                handler(wrapper.errors, e)
        if error_raised:
            raise ValidationError(wrapper.errors)
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
                 need_prepare=True,  # POST True but, json_body False
                 get_mapping=get_mapping,
                 get_validation=get_validation,
                 get_display=get_display):
        self.request = request
        self.need_prepare = need_prepare
        self.mapping = get_mapping(request, model, name)
        self.model = model
        self.name = name
        self.rawdata = None

        self.get_validation = get_validation
        self.get_display = get_display

    @reify
    def handler_lookup(self):
        return get_exception_handler_lookup(self.request)

    @reify
    def errors(self):
        return defaultdict(list)

    def prepare_validation(self, data):
        dels = []
        for k, v in data.items():
            if v == "":
                dels.append(k)
        for k in dels:
            data.pop(k)
        return self.mapping.jsondict_from_string_only_dict(data)

    def schema_validation(self, data):
        try:
            if self.need_prepare:
                data = self.prepare_validation(data)
            self.mapping.validate_all_jsondict(data)
            return data
        except Exception as e:
            handler = self.handler_lookup.lookup(e)
            handler(self.errors, e)
            raise ValidationError(self.errors)

    def validate(self, data, something=None):
        self.rawdata = data

        self.schema_validation(data)
        data = self.mapping.dict_from_jsondict(data)
        validation = self.get_validation(self.request, self.model, self.name)
        if validation is None:
            logger.info("validation is not found model=%s, name=%s", self.model, self.name)
            return data
        return validation(self, data, something)

    def to_displayobject(self, data=None):
        data = data or self.rawdata
        ob = self.mapping.object_from_dict(data, strict=False)
        return self.get_display(self.request, ob, self.name)


class Something(dict):
    __getattr__ = dict.__getitem__


@implementer(IHandlerLookup)
class HandlerLookup(object):
    def __init__(self, default_handler):
        self.relations = {}  # exc -> handler
        self.default_handler = default_handler

    def add(self, excclass, handler):
        self.relations[excclass] = handler

    def lookup(self, exc):
        start_class = type(exc)
        try:
            return self.relations[start_class]
        except KeyError:
            for cls in start_class.__mro__[1:]:
                if cls in self.relations:
                    handler = self.relations[cls]
                    self.relations[start_class] = handler
                    return handler
            handler = self.default_handler
            self.relations[start_class] = handler
            return handler


required_name_rx = re.compile(r"'(.+)'")


@provider(IExceptionHandler)
def jsonschema_error_handler(state, exc):
    for e in exc.errors:
        if e.validator == "required":
            m = required_name_rx.search(e.message)
            state[m.group(1)].append(e.message)
        else:
            state[e.path[0]].append(e.message)
    return state


@provider(IExceptionHandler)
def convertion_error_handler(state, exc):
    state[exc.name].append(exc.message)
    return state


@provider(IExceptionHandler)
def reraise_handler(state, exc):
    raise exc


def set_exception_handler_lookup(config, lookup):
    config.registry.registerUtility(lookup, IHandlerLookup, name="exception")


def get_exception_handler_lookup(request):
    return request.registry.getUtility(IHandlerLookup, name="exception")


def add_exception_handler(config, exc, handler, order=None):
    def closure():
        lookup = get_exception_handler_lookup(config)
        lookup.add(exc, handler)
    config.action(None, closure, order=order)


def includeme(config):
    config.add_directive("add_validation", add_validation)
    config.add_directive("set_exception_handler_lookup", set_exception_handler_lookup)
    config.add_directive("add_exception_handler", add_exception_handler)
    config.set_exception_handler_lookup(HandlerLookup(reraise_handler))
    config.add_exception_handler(ErrorFound, jsonschema_error_handler)
    config.add_exception_handler(ConvertionError, convertion_error_handler)
