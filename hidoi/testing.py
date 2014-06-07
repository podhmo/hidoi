# -*- coding:utf-8 -*-
from pyramid.testing import testConfig as _testConfig
import contextlib

default_widgets = set(["text", "array", "object"])  # xxx


@contextlib.contextmanager
def testConfigSlakky():
    with _testConfig(autocommit=False) as config:
        config.include("hidoi")
        config.add_fixed_widget_management(default_widgets.copy())
        config.set_default_model_module(object)
        yield config
