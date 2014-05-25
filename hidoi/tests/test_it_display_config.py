# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi import get_display
    return get_display(*args, **kwargs)


def test_it():
    from pyramid.testing import testConfig
    from hidoi.displayobject import DisplayObject
    from hidoi.tests.models import Item

    with testConfig(autocommit=False) as config:
        # configuration phase
        config.include("hidoi")
        config.add_fixed_widget_management([])
        config.scan("hidoi.tests.all_fields_are_optional")
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")

        ditem = _callFUT(request, item0)
        assert isinstance(ditem, DisplayObject)
        assert ditem.name.required is False
        assert ditem.value.required is False
        assert ditem.id.required is False
