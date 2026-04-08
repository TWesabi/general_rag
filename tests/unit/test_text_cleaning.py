import pytest

from parsers.basic_cleaning import BasicTextCleaner

cleaner = BasicTextCleaner()


@pytest.mark.parametrize(
    "input_text,expected_output",
    [
        ("#Hello", "Hello"),
        ("##Hello", "Hello"),
        ("###Hello", "Hello"),
        ("### Heading With Multiple Words", "Heading With Multiple Words"),
    ],
)
def test_strip_makedown_headers(input_text: str, expected_output: str):
    assert cleaner(input_text) == expected_output


three_blanks = ("Three blank\n\n\nlines", "Three blank\n\nlines")
four_blanks = ("Four blank\n\n\n\nlines", "Four blank\n\nlines")
five_blanks = ("Five blank\n\n\n\n\nlines", "Five blank\n\nlines")


@pytest.mark.parametrize("input_text, expected_output", [three_blanks, four_blanks, five_blanks])
def test_blankline_collapsing(input_text: str, expected_output: str):
    assert cleaner(input_text) == expected_output


@pytest.mark.parametrize(
    "input_text, expected_output",
    [("  leading", "leading"), ("trailing  ", "trailing"), ("  both  ", "both")],
)
def test_leading_trailing_white_spaces(input_text: str, expected_output: str):
    assert cleaner(input_text) == expected_output


def test_empty_string():
    input_text = ""
    assert cleaner(input_text) == ""


def test_clean_text():
    assert cleaner("Hello") == "Hello"
