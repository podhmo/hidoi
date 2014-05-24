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
