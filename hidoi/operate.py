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


def get(schema, k, val):
    if k not in schema:
        raise SchemaTreatException("{} is not found in schema(get)".format(k))
    return schema[k]


def revive(schema, ks, name="required"):
    properties = get(schema, "properties")
    required = get(schema, name)
    for k in ks:
        if k not in properties:
            raise SchemaTreatException("{} is not participants of schema(revive)".format(k))
        required.append(k)


def reorder(schema, priorities, name="required"):
    """required=[a, b, c] , priorities={a: 2, c:-10} => ((-10, c), (0, b), (2, a)) => [c, b, a]"""
    required = get(schema, name)
    candidates = [(priorities.get(e, 0), e) for e in required]
    new_required = [e for _, e in sorted(candidates, key=lambda xs: xs[0])]
    edit(schema, name, new_required)
