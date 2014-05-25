# -*- coding:utf-8 -*-
from pyramid.testing import setUp as make_config
import os.path
here = os.path.join(os.path.abspath(os.path.dirname(__file__)))

# configuration
config = make_config(autocommit=False)
config.include("hidoi")
config.set_default_model_module(object())
config.add_mako_widget_management([os.path.join(here, "./templates/helpers.mako")])
config.commit()

# runtime
from hidoi.api import get_widget_renderer
request = config
renderer = get_widget_renderer(request, "greeting")
print(renderer.render("hello"))

# output
"""
<div class="greeting">
  hello, hello
</div>
"""
