"""
Unit tests for cerberus.errors module.

"""
from io import StringIO
from unittest.mock import patch

import pytest

from cerberror.errors import ErrConverter


@pytest.fixture
def open_mock():
    with patch("cerberror.errors.open") as mock:
        yield mock


@pytest.fixture
def converter_init_mock():
    with patch("cerberror.errors.ErrConverter.__init__") as init_mock:
        init_mock.return_value = None
        err = ErrConverter()
        err._path_to_file = None
        yield err


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
