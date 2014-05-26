# -*- coding:utf-8 -*-
import sqlalchemy.types as t


def as_add_widget(name):
    def wrapper(column, sub):
        sub["widget"] = name
    wrapper.__name__ = name
    return wrapper


def includeme(config):
    def add_convertion(type_, name):
        config.add_sqla_column_convertion(type_, restriction=as_add_widget(name))
    add_convertion(t.DateTime, "datetime")
    add_convertion(t.Date, "date")
    add_convertion(t.Time, "time")
