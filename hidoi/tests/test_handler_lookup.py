# -*- coding:utf-8 -*-
def _getTarget():
    from hidoi.formwrapper import HandlerLookup
    return HandlerLookup


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def _default_not_found(exc):
    pass


def _this_handler(exc):
    pass


def _another_handler(exc):
    pass


def test_default__if_not_found():
    target = _makeOne(_default_not_found)

    class _NotRegistered(object):
        pass
    handler = target.lookup(_NotRegistered())
    assert handler == _default_not_found


def test_registered__directyly__ok():
    target = _makeOne(_default_not_found)

    class _Registered(object):
        pass
    target.add(_Registered, _this_handler)

    handler = target.lookup(_Registered())
    assert handler == _this_handler


def test_registered__inheritanced__ok():
    target = _makeOne(_default_not_found)

    class A(object):
        pass

    class B(A):
        pass

    target.add(A, _this_handler)

    handler = target.lookup(B())
    assert handler == _this_handler


def test_registered__inheritanced__cached():
    target = _makeOne(_default_not_found)

    class A(object):
        pass

    class B(A):
        pass

    target.add(A, _this_handler)

    assert B not in target.relations.keys()

    target.lookup(B())

    assert B in target.relations.keys()
