# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi.widget import iterate_mako_defs
    return iterate_mako_defs(*args, **kwargs)

import os.path
here = os.path.join(os.path.abspath(os.path.dirname(__file__)))


def test_def_is_found():
    from mako.template import Template
    template = Template(filename=os.path.join(here, "templates/helpers.mako"))

    assert template.get_def("select")
    assert template.get_def("_select")
    assert template.get_def("text")

    assert template.get_def("text").render().strip() == "text"


def test_collect_def():
    from mako.template import Template
    template = Template(filename=os.path.join(here, "templates/helpers.mako"))

    result = list(_callFUT(template))

    assert len(result) == 2
    assert sorted([name for name, _ in result]) == ["select", "text"]
    assert sorted(result)[0][1].callable_ == template.get_def("select").callable_
