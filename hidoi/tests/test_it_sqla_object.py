# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi import get_display
    return get_display(*args, **kwargs)


def test_it():
    from pyramid.testing import testConfig
    from hidoi.displayobject import DisplayObject
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfig() as config:
        # configuration phase
        config.include("hidoi")

        config.add_display(Item)
        config.add_display(Bag)

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")
        bag0 = Bag(name="1stBag", items=[item0])

        dbag = _callFUT(request, bag0)
        assert isinstance(dbag, DisplayObject)
        assert dbag.name.required is True

        for i in dbag.items.value:
            di = _callFUT(request, i)
            assert isinstance(di, DisplayObject)
            assert di.created_at.required is False

        #  get from class (using this on create form)
        ditem = _callFUT(request, Item)
        assert isinstance(ditem, DisplayObject)
        assert print(ditem.name.value) is None