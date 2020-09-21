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


def test_read_messages(open_mock):
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
    err = ErrConverter("path")

    assert err._read_messages() == result
