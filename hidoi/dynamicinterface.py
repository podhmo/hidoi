# -*- coding:utf-8 -*-
from zope.interface.interface import InterfaceClass
from zope.interface import (
    providedBy,
    implementer
)


def first_of(ob):
    try:
        return [iter(providedBy(ob)).__next__()]
    except StopIteration:
        return []


class DynamicInterfaceFactory(object):
    def __init__(self):
        self.cache = {}

    def __call__(self, cls):
        try:
            return self.cache[id(cls)]
        except KeyError:
            iface = self.create(cls)
            self.cache[id(cls)] = iface
            return iface

    def implementer(self, cls):
        return implementer(self.__call__(cls))(cls)

    def create(self, cls):
        name = "I{}".format(cls.__name__)
        return InterfaceClass(name)

_iface_factory = None


def make_interface_from_class(cls):
    global _iface_factory
    if _iface_factory is None:
        _iface_factory = DynamicInterfaceFactory()
    return _iface_factory(cls)


def add_interface(config, cls):
    cls = config.maybe_dotted(cls)
    return make_interface_from_class(cls)


def includeme(config):
    config.add_directive("dynamic_interface", add_interface)
