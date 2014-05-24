# -*- coding:utf-8 -*-
from .schema import UserSchema

@UserSchema.display("show")
def presentation(ob):
    ob.name = {"widget": "text"}
    ob.group = {"widget": "select", class_="foo", id="bar"}
    ob.add_field("foo", label="foo", format="string", class_="foo")
    ob.foo = Field()

## config
config.scan(".additional.py")

## view
o = request.presentation(Model, "show")(model)
return {"o": o}

"""
2段階にしたい。
理由は、静的にきまっているものとそうでないもの２種類があるため。
@:というか少なくとも全部dynamicで良いのでは？
"""
