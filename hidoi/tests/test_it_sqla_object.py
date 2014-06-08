# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from hidoi.api import get_display
    return get_display(*args, **kwargs)


def test_it():
    from hidoi.testing import testConfigSlakky
    from hidoi.displayobject import DisplayObject
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

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


def test_children__with_objects__normally_found():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")
        item1 = Item(name="magic portion", value="heal stress damage")
        bag0 = Bag(name="1stBag", items=[item0, item1])
        dbag = _callFUT(request, bag0)
        items = dbag.children(dbag.items, min_of_items=1)

        assert len(items) == 2
        assert list(sorted(items[0]._fieldnames)) == ['bag', 'created_at', 'id', 'name', 'value']


def test_children__without_objects__min_of_items_is_1__found():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        bag0 = Bag(name="1stBag", items=[])
        dbag = _callFUT(request, bag0)
        items = dbag.children(dbag.items, min_of_items=1)

        assert len(items) == 1
        assert list(sorted(items[0]._fieldnames)) == ['bag', 'created_at', 'id', 'name', 'value']


def test_children__without_objects__min_of_items_is_0__empty():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        bag0 = Bag(name="1stBag", items=[])
        dbag = _callFUT(request, bag0)
        items = dbag.children(dbag.items, min_of_items=0)

        assert len(items) == 0
        assert items == []


def test_child__with_child__normally_found():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")
        bag0 = Bag(name="1stBag")
        bag0.items.append(item0)
        ditem = _callFUT(request, item0)

        dbag = ditem.child(ditem.bag)
        assert list(sorted(dbag._fieldnames)) == ['id', 'items', 'name']


def test_child__without_child__min_of_items_is_1__found():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")
        ditem = _callFUT(request, item0)

        dbag = ditem.child(ditem.bag, min_of_items=1)
        assert list(sorted(dbag._fieldnames)) == ['id', 'items', 'name']


def test_child__without_child__min_of_items_is_0_None():
    from hidoi.testing import testConfigSlakky
    from hidoi.tests.models import (
        Item,
        Bag
    )
    with testConfigSlakky() as config:
        # configuration phase
        config.add_display(Item)
        config.add_display(Bag)
        config.commit()

        # runtime phase
        request = config
        item0 = Item(name="portion", value="heal damage")
        ditem = _callFUT(request, item0)

        dbag = ditem.child(ditem.bag, min_of_items=0)
        assert dbag is None


