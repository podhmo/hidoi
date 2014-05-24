pyramid_displayobject
========================================

.. code:: python

    # -*- coding:utf-8 -*-
    import sqlalchemy as sa
    import sqlalchemy.orm as orm
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()


    class Item(Base):
        __tablename__ = "items"
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(255), default="", nullable=False)
        value = sa.Column(sa.String(255), default="", nullable=False)
        created_at = sa.Column(sa.DateTime())
        bag_id = sa.Column(sa.Integer, sa.ForeignKey("bags.id"))
        bag = orm.relationship("Bag", backref="items", uselist=False)


    class Bag(Base):
        __tablename__ = "bags"
        id = sa.Column(sa.Integer, primary_key=True)
        name = sa.Column(sa.String(255), default="", nullable=False)


    def _callFUT(*args, **kwargs):
        from pyramid_displayobject import get_display
        return get_display(*args, **kwargs)


    def test_it():
        from pyramid.testing import testConfig
        from pyramid_displayobject.displayobject import DisplayObject

        with testConfig() as config:
            # configuration phase
            config.include("pyramid_displayobject")

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


