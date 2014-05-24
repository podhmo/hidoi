# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from pyramid_displayobject import get_display
    return get_display(*args, **kwargs)


def test_it():
    from pyramid.testing import testConfig
    from pyramid_displayobject.displayobject import DisplayObject
    from pyramid_displayobject.tests.models import Item

    with testConfig() as config:
        # configuration phase
        config.include("pyramid_displayobject")
        config.scan("pyramid_displayobject.tests.all_fields_are_optional")
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")

        ditem = _callFUT(request, item0)
        assert isinstance(ditem, DisplayObject)
        assert ditem.name.required is False
        assert ditem.value.required is False
        assert ditem.id.required is False
