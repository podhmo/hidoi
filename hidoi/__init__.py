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


def inspect_model_action(config, model, name, order, val=None):
    try:
        q = getattr(config.registry, "modelaction_list")
        modelname = config.maybe_dotted(model).__name__
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
    config.include(".dynamicinterface")

    config.include(".schema")
    config.include(".widget")

    config.include(".displayobject")
    config.include(".mapping")
    config.include(".formwrapper")

    config.include(".verify")
    parse_option_from_config(config, settings_prefix="hidoi.")
