# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from sqlalchemy.ext.declarative.api import DeclarativeMeta


def model_of(object_or_class):
    if isinstance(object_or_class, DeclarativeMeta):
        return object_or_class  # class
    else:
        return object_or_class.__class__  # object


def funcname(fn):
    return "{}:{}".format(fn.__module__, fn.__name__)


class RepeatableSetQueue(object):
    def __init__(self, name=""):
        self.name = name
        self.cache = {}
        self.result = []
        self.q = []

    def add(self, v, order=0):
        if self.result:
            raise Exception("already running. so cannot add")
        pk = id(v)
        if pk not in self.cache:
            self.cache[pk] = 1
            self.q.append((order, v))

    def __iter__(self):
        if self.result:
            for e in self.result:
                yield e
        else:
            logger.info("*validation(%s): is starting. length=%d", self.name, len(self.q))
            itr = sorted(self.q, key=lambda x: x[0])
            for _, e in itr:
                self.result.append(e)
                yield e
            logger.info("*validation(%s): is finished. length=%d", self.name, len(self.result))
