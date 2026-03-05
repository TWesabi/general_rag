from pathlib import Path

import pytest

from src.parsers.parser_pdf import parse_document

PARSED_RESULT = parse_document(Path("docs/to_index/Test_Text.pdf"))


def test_parse_document_file_not_found():
    fake_path = Path("does/not/exist.pdf")
    with pytest.raises(FileNotFoundError):
        parse_document(file_path=fake_path)


def test_parse_document_returns_expected_keys():
    assert set(PARSED_RESULT.keys()) == {
        "local_path",
        "status",
        "timestamp",
        "doc_name",
        "num_pages",
        "text_content",
        "table_count",
        "has_tables",
        "mimetype",
        "binary_hash",
        "filename",
    }


def test_parse_document_text_content_is_nonempty_string():
    assert len(PARSED_RESULT["text_content"]) > 0
    assert isinstance(PARSED_RESULT["text_content"], str)


def test_parse_document_num_pages_is_positive():
    assert isinstance(PARSED_RESULT["num_pages"], int)
    assert PARSED_RESULT["num_pages"] > 0
