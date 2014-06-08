# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from collections import OrderedDict


def model_of(object_or_class):
    if isinstance(object_or_class, DeclarativeMeta):
        return object_or_class  # class
    elif isinstance(object_or_class, type):
        return object_or_class
    else:
        return object_or_class.__class__  # object


def funcname(fn):
    if fn is None:
        return "None"
    return "{}:{}".format(fn.__module__, fn.__name__)


def wrap_repetable_set_queue(D, name, k, val):
    v = D.get(k)
    if v is None:
        v = D[k] = RepeatableSetQueue(name)
    elif isinstance(v, RepeatableSetQueue):
        v.add(val)
    else:
        D[k] = q = RepeatableSetQueue(name)
        q.add(v)
        q.add(val)


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

    def __call__(self, *args, **kwargs):
        for fn in self:
            fn(*args, **kwargs)


def get_pairs_iterator(xs):
    if hasattr(xs, "items"):
        for k, v in xs.items():
            yield k, v
    elif xs and hasattr(xs[0], "items") and len(xs[0]) == 1:
        for x in xs:
            for k, v in x.items():
                yield k, v
    else:
        for k, v in xs:
            yield k, v


def insertion(ds, k, v):
    for d in ds:
        if k not in d:
            d[k] = v
            return
    ds.append({k: v})


def insertion_nested(r, xs, v, factory=OrderedDict):
    target = r
    prev = None
    for x in xs[:-1]:
        if x not in target:
            target[x] = factory()
        prev = target
        target = target[x]
    if isinstance(target, list):
        insertion(target, xs[-1], v)
    elif xs[-1] in target:
        prev[xs[-2]] = [target, {xs[-1]: v}]
    else:
        target[xs[-1]] = v
    return r


def nested_from_flatten(D, splitter=".", factory=OrderedDict):
    r = factory()
    for k, v in get_pairs_iterator(D):
        if splitter not in k:
            r[k] = v
        else:
            xs = k.split(splitter)
            insertion_nested(r, xs, v, factory)
    return r
