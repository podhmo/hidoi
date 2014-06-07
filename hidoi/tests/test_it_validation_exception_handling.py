# -*- coding:utf-8 -*-
def _getTarget():
    from hidoi.formwrapper import FormWrapper
    return FormWrapper


def _makeRequest(config):
    from pyramid.request import Request
    request = Request.blank("/")
    request.registry = config.registry
    return request


def _makeOne(*args, **kwargs):
    return _getTarget()(*args, **kwargs)


def test_schema_validation_success():
    from pyramid.testing import testConfig
    from . import models
    with testConfig() as config:
        config.include("hidoi.dynamicinterface")
        config.include("hidoi.modelmodule")
        config.include("hidoi.schema")
        config.include("hidoi.displayobject")
        config.include("hidoi.formwrapper")

        config.set_default_model_module(models)
        config.add_display(models.Bag)

        request = _makeRequest(config)
        target = _makeOne(request, models.Bag)

        data = {"name": "foo", "id": 1}
        result = target.validate(data)

        assert result == {"name": "foo", "id": 1, "items": []}


def test_schema_validation_missing_required__error():
    import pytest
    from hidoi.formwrapper import ValidationError
    from hidoi.testing import testConfigSlakky
    from . import models

    with testConfigSlakky() as config:
        config.set_default_model_module(models)
        config.add_display(models.Bag)
        config.commit()

        request = _makeRequest(config)
        target = _makeOne(request, models.Bag)

        data = {"name": "foo"}

        with pytest.raises(ValidationError):
            target.validate(data)


def test_schema_validation_invalid_type__error():
    import pytest
    from hidoi.formwrapper import ValidationError
    from hidoi.testing import testConfigSlakky
    from . import models

    with testConfigSlakky() as config:
        config.set_default_model_module(models)
        config.add_display(models.Bag)
        config.commit()

        request = _makeRequest(config)
        target = _makeOne(request, models.Bag)

        data = {"name": "foo", "id": "foo"}

        with pytest.raises(ValidationError):
            target.validate(data)
