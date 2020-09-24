"""
Unit tests for cerberus.errors module.

"""
from io import StringIO
from unittest.mock import patch

import pytest

from cerberror.errors import ErrConverter


path_to_file = "path/to/file"


@pytest.fixture
def open_mock():
    with patch("cerberror.errors.open") as mock:
        yield mock


@pytest.fixture
def converter_init_mock():
    with patch("cerberror.errors.ErrConverter.__init__") as init_mock:
        init_mock.return_value = None
        converter = ErrConverter(path_to_file)
        converter._path_to_file = path_to_file
        yield converter


@pytest.fixture
def converter_report_error_mock(converter_init_mock):
    with patch("cerberror.errors.ErrConverter._report_error"):
        yield converter_init_mock


def test_read_predefined_messages(converter_init_mock, open_mock):
    stream = StringIO(
        "# path code message\n"
        "(1, 2, 'a')    67    \"My custom message for {{code}}\"\n"
        "# This is a comment\n"
        "     ('a', 'b', 'c') 2 \"Random message {{key}}\"\n"
        '(99,)   123 "Cannot be..."\n'
        "('key_a', 'key_b', 'key_c') 42 \n"
        "(7, 1, 'abc') 24 \"A new message (updated)\"\n"
        "('key_a', 'key_b', '7') 30  \"The {{last}} one message!\"\n"
    )
    result = (
        ((1, 2, "a"), 67, "My custom message for {{code}}"),
        (("a", "b", "c"), 2, "Random message {{key}}"),
        ((99,), 123, "Cannot be..."),
        ((7, 1, "abc"), 24, "A new message (updated)"),
        (("key_a", "key_b", "7"), 30, "The {{last}} one message!"),
    )
    open_mock.return_value = stream

    assert converter_init_mock._read_predefined_messages() == result


def test_read_predefined_messages_no_messages_found(converter_report_error_mock, open_mock):
    stream = StringIO(
        "# path code message\n"
        "!(1, 2, 'a')    67    \"My custom message for {{code}}\"\n"
        "# This is a comment\n"
        '$  (99,)   123 "Cannot be..."\n'
    )
    open_mock.return_value = stream
    converter_report_error_mock._read_predefined_messages()

    converter_report_error_mock._report_error.assert_called_once_with(
        f"No customized messages have been found in '{path_to_file}' file"
    )


def test_read_predefined_messages_file_not_found_error(converter_report_error_mock, open_mock):
    open_mock.side_effect = FileNotFoundError
    converter_report_error_mock._read_predefined_messages()

    converter_report_error_mock._report_error.assert_called_once_with(
        f"File '{path_to_file}' does not exist"
    )
