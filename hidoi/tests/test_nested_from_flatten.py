# -*- coding:utf-8 -*-
import pytest

candidates = [
    [{}, "a.b.c", 10, {"a": {"b": {"c": 10}}}],
    [{"a": {"b": {"c": 10}}}, "a.b.c", 20, {"a": {"b": [{"c": 10}, {"c": 20}]}}],
    [{"a": {"b": [{"c": 10}, {"c": 20}]}}, "a.b.b", 10, {"a": {"b": [{"c": 10, "b": 10}, {"c": 20}]}}],
    [{"a": {"b": [{"c": 10}, {"c": 20}]}}, "a.b.c", 30, {"a": {"b": [{"c": 10}, {"c": 20}, {"c": 30}]}}],
    [{}, "a.b", 10, {"a": {"b": 10}}],
    [{"a": {"b": 10}}, "a.b", 20, {"a": [{"b": 10}, {"b": 20}]}],
    [{"a": [{"b": 10}, {"b": 20}]}, "a.b", 30, {"a": [{"b": 10}, {"b": 20}, {"b": 30}]}],
]


@pytest.mark.parametrize("before, k, v, after", candidates)
def test_insertion_nested(before, k, v, after):
    from hidoi.langhelpers import insertion_nested
    xs = k.split(".")
    result = insertion_nested(before, xs, v, dict)
    assert result == after


candidates2 = [
    [{}, {}],
    [{"a": 1}, {"a": 1}],
    [[{"a": 1}, {"a": 2}], {"a": 2}],  # xxx
    [{"a.b": 10}, {"a": {"b": 10}}],
    [[{"a.b": 10}, {"a.b": 20}], {"a": [{"b": 10}, {"b": 20}]}],
]


@pytest.mark.parametrize("before, after", candidates2)
def test_nested_from_flatten(before, after):
    from hidoi.langhelpers import nested_from_flatten
    result = nested_from_flatten(before, factory=dict)
    assert result == after
