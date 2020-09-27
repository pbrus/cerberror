"""
Unit tests for cerberror.trans module.

"""
from unittest.mock import Mock, patch, PropertyMock

import pytest

from cerberror.trans import Translator
from tests.test_errors import path_to_file, ValidationError


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
def init_mock():
    with patch("cerberror.trans.Translator.__init__", return_value=None) as mock:
        yield mock


@pytest.fixture
def report_error_mock():
    with patch("cerberror.trans.Translator._report_error") as mock:
        yield mock


@pytest.fixture
def translator_init_report_error_mock(
    init_mock, report_error_mock, path_finder_init_mock, path_finder_paths_mock
):
    translator = Translator(Mock(), path_to_file)
    translator._validator = Mock()
    yield translator


def test_get_paths(translator_init_report_error_mock, report_error_mock, path_finder_paths_mock):
    translator_init_report_error_mock.get_paths()

    path_finder_paths_mock.assert_called_once()
    report_error_mock.assert_not_called()


def test_get_paths_fail(
    translator_init_report_error_mock, report_error_mock, path_finder_paths_mock
):
    path_finder_paths_mock.return_value = tuple()
    translator_init_report_error_mock.get_paths()

    path_finder_paths_mock.assert_called_once()
    report_error_mock.assert_called_once_with("No path was found")


@pytest.mark.parametrize(
    "errors, result",
    [
        ("Error occurred", ["Error occurred"]),
        (["Error1", "Error2", "Error3"], ["Error1", "Error2", "Error3"]),
    ],
)
def test_report_error(errors, result):
    err = "messages"
    validator = ValidationError({"errors": err})
    translator = Translator(validator, path_to_file)

    if isinstance(errors, str):
        translator._report_error(errors)
    else:
        translator._report_error(*errors)

    assert translator._any_error
    assert translator._error_list == result
    assert translator._errors == err
