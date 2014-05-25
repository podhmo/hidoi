# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import IWidgetManagement
from pyramid.path import AssetResolver


default_widgets = ["text", "date-time"]  # xxx


@implementer(IWidgetManagement)
class WidgetManagement(object):
    def __init__(self, defaults=default_widgets):
        self.formats = set(default_widgets[:])

    def is_correct(self, widget):
        return widget in self.formats

    def add(self, widget):
        self.formats.add(widget)


def add_mako_widget_management(config, widget_template_file_list):
    formats = []
    resolver = AssetResolver()
    for assetspec in widget_template_file_list:
        path = resolver.resolve(assetspec).abspath()
        formats.extend(get_formats_from_mako_file(path))
    config.registry.registerUtility(WidgetManagement(formats), IWidgetManagement)


def add_fixed_widget_management(config, formats):
    config.registry.registerUtility(WidgetManagement(formats), IWidgetManagement)

def get_formats_from_mako_file(path):
    return []


def includeme(config):
    config.add_directive("add_mako_widget_management", add_mako_widget_management)
    config.add_directive("add_fixed_widget_management", add_fixed_widget_management)
