# -*- coding:utf-8 -*-
def _callFUT(config, type_):
    from hidoi.schema import get_schema_factory
    D = {}
    column = None
    target = get_schema_factory(config)
    target._add_restriction_if_found(D, column, type_)
    return D


def test_prepare():
    from hidoi.testing import testConfigSlakky
    import sqlalchemy.types as t

    with testConfigSlakky() as config:
        config.commit()

        result = _callFUT(config, t.DateTime)
        assert "widget" not in result
        assert result["format"] == "date-time"  # added by default hook


def test_it():
    from hidoi.testing import testConfigSlakky
    import sqlalchemy.types as t

    with testConfigSlakky() as config:
        config.include("hidoi.custom.html5")
        config.commit()

        result = _callFUT(config, t.DateTime)
        assert result["widget"] == "datetime"
        assert result["format"] == "date-time"  # added by default hook
