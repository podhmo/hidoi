# -*- coding:utf-8 -*-
from pyramid.exceptions import ConfigurationError
from .interfaces import (
    IWidgetManagement,
    IDisplayObjectFactory
)
"""
memo:
# configuration phases: a lower phase number means the actions associated
# with this phase will be executed earlier than those with later phase
# numbers.  The default phase number is 0, FTR.

PHASE1_CONFIG = -20
PHASE2_CONFIG = -10
"""

LAST_PHASE_CONFIG = 10


def register_verify_configuration(config):
    # if you testing config.include("hidoi"). then autocommit=False is requried.
    def closure():
        fmt = "{iface} is not registered. forget to call config.{directive}?"
        q = config.registry.queryUtility
        if q(IWidgetManagement) is None:
            raise ConfigurationError(fmt.format(iface="IWidgetManagement", directive="add_mako_widget_management"))

        if q(IDisplayObjectFactory) is None:
            raise ConfigurationError(fmt.format(iface="IDisplayObjectFactory", directive="add_display_object_factory"))
    config.action(None, closure, order=LAST_PHASE_CONFIG)


def includeme(config):
    register_verify_configuration(config)
