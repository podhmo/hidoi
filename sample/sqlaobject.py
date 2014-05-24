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


from pyramid_displayobject import (
    get_display,
    DisplayObjectFactory,
    FieldFactory,
    WidgetManagement,
)
from pyramid.testing import setUp as make_configurator

config = make_configurator()
config.include("pyramid_displayobject")

config.add_display(Item)
config.add_display(Bag)


item0 = Item(name="portion", value="heal damage")
bag0 = Bag(name="1stBag")
bag0.items.append(item0)

ditem = get_display(config, item0)


print(ditem)
print(ditem.id)
print(ditem.name)
print(ditem.value)
print(ditem.created_at)


dbag = get_display(config, bag0)
print(dbag._fieldnames)
print([get_display(config, i) for i in dbag.items.value])

