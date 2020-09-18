"""
Unit tests for cerberus.path_finder module.

"""
from unittest.mock import Mock

import pytest

from cerberror.path_finder import PathFinder


@pytest.fixture
def path_finder() -> PathFinder:
    errors = Mock()
    yield PathFinder(errors)


@pytest.mark.parametrize(
    "data, result",
    [
        ({"a": 1, "b": 2, "c": [3, 4]}, {"a": 1, "b": 2, "c": [3, 4]}),
        ([{"a": 1, "b": [2, 3, 4]}], {"a": 1, "b": [2, 3, 4]}),
        ((1, 2, 3, "a"), (1, 2, 3, "a")),
        ([[["a", 1]]], ["a", 1]),
    ],
)
def test_skip_list(data, result):
    assert PathFinder.skip_lists(data) == result


@pytest.mark.parametrize(
    "dct, item, result",
    [([{"a": 1, "b": 2}], "a", 1), ([[{"c": 3, "d": 4}]], "c", 3), ({5: "e"}, 5, "e")],
)
def test_getitem_skipping_lists(path_finder, dct, item, result):
    assert path_finder._getitem_skipping_lists(dct, item) == result


@pytest.mark.parametrize(
    "dct, path, result",
    [
        ([{"a": [{"b": 1, "c": 2, "d": [{"e": 3}]}]}], ("a", "d", "e"), 3),
        ({1: {2: 1, 3: [[{4: 1, "key": {7: 0}}]]}}, (1, 3, "key", 7), 0),
        ([{"a": [{"b": {"c": [1, 2], "d": 0}}]}], ("a", "b", "c"), [1, 2]),
        ({"a": [{"b": 1, "c": 2, "d": [{"e": 3}, 4]}]}, ("a", "d"), [{"e": 3}, 4]),
    ],
)
def test_get_element_by_path(path_finder, dct, path, result):
    assert path_finder._get_element_by_path(dct, path) == result


@pytest.mark.parametrize(
    "dct, path, result",
    [
        (
            [{1: 2, 3: {"a": 4, "b": [{5: 0, 6: "value"}]}}],
            (3, "b", 6),
            [{1: 2, 3: {"a": 4, "b": [{5: 0}]}}],
        ),
        ({1: [{"a": {2: "b"}}]}, (1, "a", 2), {1: [{"a": {}}]}),
        (
            [[{1: "a", 2: [-1, 0, 1], "b": [{3: "value", 4: [{5: 6}]}]}]],
            ("b", 4, 5),
            [[{1: "a", 2: [-1, 0, 1], "b": [{3: "value", 4: [{}]}]}]],
        ),
        (
            [[{1: "a", 2: [-1, 0, 1], "b": [{3: "value", 4: [{5: 6}]}]}]],
            ("b",),
            [[{1: "a", 2: [-1, 0, 1]}]],
        ),
    ],
)
def test_del_element_by_path(path_finder, dct, path, result):
    path_finder._del_element_by_path(dct, path)
    assert dct == result


@pytest.mark.parametrize(
    "dct, result",
    [
        ([{1: "a", 2: [-1, 0, 1], "b": [{3: "value", 4: [{}]}]}], ("b", 4)),
        ({1: {"a": [{2: "b", 3: {4: "value"}}]}}, (1, "a", 3, 4)),
        ([{1: {"a": [{2: "b", 3: [{}]}]}}], (1, "a", 3)),
        (
            {"a": 1, "b": 2, "c": {3: {"aa": 4, "bb": [{"cc": 1}, "value"]}}},
            ("c", 3, "bb"),
        ),
    ],
)
def test_get_path_to_element(path_finder, dct, result):
    assert path_finder._get_path_to_element(dct) == result
