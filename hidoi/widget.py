# -*- coding:utf-8 -*-
from zope.interface import implementer
from .interfaces import IWidgetManagement

default_widgets = ["text", "date-time"]  # xxx


@implementer(IWidgetManagement)
class WidgetManagement(object):
    def __init__(self, defaults=default_widgets):
        self.formats = set(default_widgets[:])

    def is_correct(self, widget):
        return widget in self.formats

    def add(self, widget):
        self.formats.add(widget)


def includeme(config):
    config.registry.registerUtility(WidgetManagement(), IWidgetManagement)  # xxx
