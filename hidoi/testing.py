# -*- coding:utf-8 -*-
from pyramid.testing import testConfig as _testConfig
import contextlib


@contextlib.contextmanager
def testConfigSlakky():
    with _testConfig(autocommit=False) as config:
        config.include("hidoi")
        config.add_fixed_widget_management([])
        config.set_default_model_module(object)
        yield config
