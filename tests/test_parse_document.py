from pathlib import Path

import pytest

from src.parsers.parser_pdf import PdfParser

parser = PdfParser()

PARSED_RESULT = parser(Path("tests/data/Test_Sample.pdf"))


def test_parse_document_file_not_found():
    fake_path = Path("does/not/exist.pdf")
    with pytest.raises(FileNotFoundError):
        parser(file_path=fake_path)


@pytest.mark.integration
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


@pytest.mark.integration
def test_parse_document_text_content_is_nonempty_string():
    assert len(PARSED_RESULT["text_content"]) > 0
    assert isinstance(PARSED_RESULT["text_content"], str)


@pytest.mark.integration
def test_parse_document_num_pages_is_positive():
    assert isinstance(PARSED_RESULT["num_pages"], int)
    assert PARSED_RESULT["num_pages"] > 0
