# -*- coding:utf-8 -*-
def set_default_model_module(config, module):
    from .interfaces import IModelModule
    module = config.maybe_dotted(module)
    config.registry.registerUtility(module, IModelModule)


def includeme(config):
    config.add_directive("set_default_model_module", set_default_model_module)
    config.include(".dynamicinterface")

    config.include(".schema")
    config.include(".widget")

    config.include(".displayobject")

    config.include(".verify")
