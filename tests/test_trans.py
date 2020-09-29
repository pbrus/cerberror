"""
Unit tests for cerberror.trans module.

"""
from unittest.mock import Mock, patch, PropertyMock

import pytest

from cerberror.trans import Translator, ErrConverter
from tests.test_errors import path_to_file, ValidationError


class Validator:
    """Class emulating Validator of Cerberus."""

    def __init__(self, dct):
        self.document_error_tree = DocumentErrorTree(dct)


class DocumentErrorTree:
    """Class emulating Document Error Tree of Cerberus."""

    def __init__(self, dct):
        self._dct = self._convert(dct)

    @staticmethod
    def _convert(dct):
        for key in dct:
            dct.update({key: [ValidationError(i) for i in dct[key]]})

        return dct

    def fetch_errors_from(self, path):
        return self._dct[path]


@pytest.fixture
def path_finder_paths_mock():
    with patch(
        "cerberror.trans.PathFinder.paths", return_value=None, new_callable=PropertyMock
    ) as mock:
        yield mock


@pytest.fixture
def path_finder_init_mock(path_finder_paths_mock):
    with patch("cerberror.trans.PathFinder.__init__", return_value=None) as mock:
        yield mock


@pytest.fixture
def converter_records_mock():
    with patch(
        "cerberror.trans.ErrConverter.user_defined_records",
        return_value=None,
        new_callable=PropertyMock,
    ) as mock:
        yield mock


@pytest.fixture
def converter_init_mock(converter_records_mock):
    with patch("cerberror.trans.ErrConverter.__init__", return_value=None) as mock:
        yield mock


@pytest.fixture
def init_mock():
    with patch("cerberror.trans.Translator.__init__", return_value=None) as mock:
        yield mock


@pytest.fixture
def report_error_mock():
    with patch("cerberror.trans.Translator._report_error") as mock:
        yield mock


@pytest.fixture
def translator_init_report_error_mock(
    init_mock,
    report_error_mock,
    path_finder_init_mock,
    path_finder_paths_mock,
    converter_init_mock,
    converter_records_mock,
):
    translator = Translator(Mock(), path_to_file)
    translator._path_to_file = path_to_file
    translator._converter = ErrConverter(path_to_file)
    translator._validator = Mock()
    yield translator


# ==================== TESTS ====================


def test_get_paths(translator_init_report_error_mock, report_error_mock, path_finder_paths_mock):
    translator_init_report_error_mock._get_paths()

    path_finder_paths_mock.assert_called_once()
    report_error_mock.assert_not_called()


def test_get_paths_fail(
    translator_init_report_error_mock, report_error_mock, path_finder_paths_mock
):
    path_finder_paths_mock.return_value = tuple()
    translator_init_report_error_mock._get_paths()

    path_finder_paths_mock.assert_called_once()
    report_error_mock.assert_called_once_with("No path was found")


def test_get_records(translator_init_report_error_mock, converter_records_mock):
    translator_init_report_error_mock._get_records()

    converter_records_mock.assert_called_once()


@pytest.mark.parametrize(
    "errors, result",
    [
        ("Error occurred", ["Error occurred"]),
        (["Error1", "Error2", "Error3"], ["Error1", "Error2", "Error3"]),
    ],
)
def test_report_error(errors, result):
    translator = Translator({}, path_to_file)

    if isinstance(errors, str):
        translator._report_error(errors)
    else:
        translator._report_error(*errors)

    assert translator._any_error
    assert translator._error_list == result


@pytest.mark.parametrize(
    "paths, pre_errors, records, sep, result",
    [
        (
            (("a", "b", "c", "d"), ("a", "b", "c", "e"), ("a", "b", "bb")),
            {
                ("a", "b", "c", "d"): [{"code": 66, "value": 3, "constraint": 5}],
                ("a", "b", "c", "e"): [{"code": 36}],
                ("a", "b", "bb"): [
                    {"code": 66, "value": 6, "constraint": 10},
                    {"code": 68, "value": 5, "constraint": [1, 2, 3]},
                ],
            },
            (
                (("a", "b", "c", "d"), 66, "{{value}} is less than {{constraint}}"),
                (("a", "b", "c", "e"), 36, "This number should be type of integer, bro!"),
                (("a", "b", "bb"), 66, "{{value}} cannot be less than {{constraint}}"),
                (("a", "b", "bb"), 68, "Only allowed values are {{constraint}}, not {{value}}"),
            ),
            " -> ",
            {
                "a -> b -> c -> d": ["3 is less than 5"],
                "a -> b -> c -> e": ["This number should be type of integer, bro!"],
                "a -> b -> bb": [
                    "6 cannot be less than 10",
                    "Only allowed values are [1, 2, 3], not 5",
                ],
            },
        ),
        (
            ((1, 2, "a"), ("b",), ("c", "d", "e")),
            {
                (1, 2, "a"): [{"code": 11, "value": 15.5, "type": "float"}],
                ("b",): [{"code": 2}, {"code": 404}],
                ("c", "d", "e"): [{"code": 28, "value": "Python", "constraint": "string"}],
            },
            (
                ((1, 2, "a"), 11, "{{value}} cannot be {{type}}"),
                (("b",), 2, "Awesome error"),
                (("c", "d", "e"), 28, "Value {{value}} is a {{constraint}}, it shouldn't be!"),
                (("b",), 404, "Another awesome error"),
            ),
            ".",
            {
                "1.2.a": ["15.5 cannot be float"],
                "b": ["Awesome error", "Another awesome error"],
                "c.d.e": ["Value Python is a string, it shouldn't be!"],
            },
        ),
    ],
)
def test_translate(
    translator_init_report_error_mock, report_error_mock, paths, pre_errors, records, sep, result
):
    translator_init_report_error_mock._validator = Validator(pre_errors)
    translator_init_report_error_mock._paths = paths
    translator_init_report_error_mock._records = records

    translator_init_report_error_mock._translate(sep)

    assert translator_init_report_error_mock._errors == result
    report_error_mock.assert_not_called()


@pytest.mark.parametrize(
    "paths, pre_errors, records, calls",
    [
        (
            (("a", "b", "c", "d"), ("a", "b", "c", "e"), ("a", "b", "bb")),
            {
                ("a", "b", "c", "d"): [{"code": 66, "value": 3, "constraint": 5}],
                ("a", "b", "c", "e"): [{"code": 36}],
                ("a", "b", "bb"): [
                    {"code": 66, "value": 6, "constraint": 10},
                    {"code": 68, "value": 5, "constraint": [1, 2, 3]},
                ],
            },
            (
                (("a", "b", "c", "d"), 66, "{{value}} is less than {{constraint}}"),
                (("a", "b", "bb"), 66, "{{value}} cannot be less than {{constraint}}"),
            ),
            2,
        ),
        (
            ((1, 2, "a"), ("b",), ("c", "d", "e")),
            {
                (1, 2, "a"): [{"code": 11, "value": 15.5, "type": "float"}],
                ("b",): [{"code": 2}, {"code": 404}],
                ("c", "d", "e"): [{"code": 28, "value": "Python", "constraint": "string"}],
            },
            (
                ((1, 2, "a"), 11, "{{value}} cannot be {{type}}"),
                (("b",), 2, "Awesome error"),
                (("c", "d", "e"), 28, "Value {{value}} is a {{constraint}}, it shouldn't be!"),
            ),
            1,
        ),
    ],
)
def test_translate_fail(
    translator_init_report_error_mock, report_error_mock, paths, pre_errors, records, calls
):
    translator_init_report_error_mock._validator = Validator(pre_errors)
    translator_init_report_error_mock._paths = paths
    translator_init_report_error_mock._records = records

    translator_init_report_error_mock._translate(">>")

    assert report_error_mock.call_count == calls
