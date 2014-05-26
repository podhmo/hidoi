# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import (
    IWidgetManagement,
    IWidgetRenderer
)
from pyramid.path import AssetResolver
from pyramid.exceptions import ConfigurationError
from mako.template import Template as MakoTemplate


@implementer(IWidgetManagement)
class WidgetManagement(object):
    def __init__(self, widgets):
        self.widgets = widgets

    def is_correct(self, widget):
        return widget in self.widgets

    def add(self, widget):
        self.formats.add(widget)


def get_widget_renderer(request, name="text"):
    def_ = request.registry.getUtility(IWidgetRenderer, name=name)
    return def_


def add_mako_widget_management(config, widget_template_file_list, overwrite=False):
    formats = set()
    resolver = AssetResolver()
    for assetspec in widget_template_file_list:
        path = resolver.resolve(assetspec).abspath()
        for name, def_ in get_name_def_pairs_from_mako_file(path):
            if not overwrite and name in formats:
                raise ConfigurationError("widget {} is existed, already. conflicted".format(name))
            formats.add(name)
        config.registry.registerUtility(def_, IWidgetRenderer, name=name)
    config.registry.registerUtility(WidgetManagement(formats), IWidgetManagement)


def add_fixed_widget_management(config, formats):
    config.registry.registerUtility(WidgetManagement(formats), IWidgetManagement)


def get_name_def_pairs_from_mako_file(path):
    template = MakoTemplate(filename=path)
    return iterate_mako_defs(template)


def iterate_mako_defs(template):
    for k in template.module.__dict__.keys():
        if k.startswith("render_"):
            if k.startswith("render__") or k == "render_body":
                continue
            if hasattr(template.module, k):
                name = k.split("render_", 1)[1]
                yield name, template.get_def(name)


def includeme(config):
    config.add_directive("add_mako_widget_management", add_mako_widget_management)
    config.add_directive("add_fixed_widget_management", add_fixed_widget_management)
