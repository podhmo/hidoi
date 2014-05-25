# -*- coding:utf-8 -*-
class SchemaTreatException(Exception):
    pass


def edit(schema, k, val):
    if k not in schema:
        raise SchemaTreatException("{} is not found in schema(edit)".format(k))
    schema[k] = val


def default(schema, k, val):
    if k in schema:
        return
    schema[k] = val


def new(schema, k, val):
    if k in schema:
        raise SchemaTreatException("{} is found in schema(create)".format(k))
    schema[k] = val


def get(schema, k):
    if k not in schema:
        raise SchemaTreatException("{} is not found in schema(get)".format(k))
    return schema[k]


def allvisible(schema, name="visible"):
    revive(schema, [k for k in schema["properties"]], name)


def revive(schema, ks, name="visible"):
    properties = get(schema, "properties")
    visible = get(schema, name)
    for k in ks:
        if k not in properties:
            raise SchemaTreatException("{} is not participants of schema(revive)".format(k))
        visible.append(k)


def add(schema, k, name="visible"):
    visible = get(schema, name)
    if k in visible:
        return
    visible.append(k)


def remove(schema, k, name="visible"):
    visible = get(schema, name)
    try:
        i = visible.index(k)
        visible.pop(i)
    except ValueError:
        pass


def reorder(schema, priorities, name="visible"):
    """visible=[a, b, c] , priorities={a: 2, c:-10} => ((-10, c), (0, b), (2, a)) => [c, b, a]"""
    visible = get(schema, name)
    candidates = [(priorities.get(e, 0), e) for e in visible]
    new_visible = [e for _, e in sorted(candidates, key=lambda xs: xs[0])]
    edit(schema, name, new_visible)
