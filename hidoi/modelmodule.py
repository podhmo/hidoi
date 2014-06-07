# -*- coding:utf-8 -*-
# todo rename
import logging
logger = logging.getLogger(__name__)
from collections import defaultdict


def set_default_model_module(config, module):
    from .interfaces import IModelModule
    module = config.maybe_dotted(module)
    config.registry.registerUtility(module, IModelModule)

c = defaultdict(float)


def inspect_model_action(config, model, name, order, val=None):
    try:
        q = getattr(config.registry, "modelaction_list")
        modelname = config.maybe_dotted(model).__name__
        if order == 0:
            k = (model, name, val[0])
            order = c[k]
            c[k] += 0.01
        q.add((modelname, name, order, val))
    except AttributeError:
        config.registry.modelaction_list = set()
        return inspect_model_action(config, model, name, order, val)
    except TypeError as e:
        from pyramid.exceptions import ConfigurationError
        raise ConfigurationError("{}: value={}".format(e.args[0], val))


def includeme(config):
    config.add_directive("set_default_model_module", set_default_model_module)
    config.add_directive("inspect_model_action", inspect_model_action)
