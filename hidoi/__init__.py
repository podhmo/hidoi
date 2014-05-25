# -*- coding:utf-8 -*-
def set_default_model_module(config, module):
    from .interfaces import IModelModule
    module = config.maybe_dotted(module)
    config.registry.registerUtility(module, IModelModule)


def parse_option_from_config(config, settings_prefix="hidoi."):
    settings = config.registry.settings

    def sget(name, default=None):
        return settings.get(settings_prefix + name, default)

    if sget("model.module"):
        config.set_default_model_module(sget("model.module"))

    if sget("widget.template_path"):
        config.add_mako_widget_management([sget("widget.template_path")])


def includeme(config):
    config.add_directive("set_default_model_module", set_default_model_module)
    config.include(".dynamicinterface")

    config.include(".schema")
    config.include(".widget")

    config.include(".displayobject")

    config.include(".verify")
    parse_option_from_config(config, settings_prefix="hidoi.")
