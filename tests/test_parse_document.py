from pathlib import Path

import pytest

from src.parsers.parser_pdf import PdfParser
from src.schemas.document import DocumentMetadata, DocumentSchema


@pytest.fixture(scope="session")
def parser():
    return PdfParser()


@pytest.fixture(scope="session")
def parsed_result(parser):
    return parser(Path("tests/data/Test_Sample.pdf"))


def test_parse_document_file_not_found(parser):
    fake_path = Path("does/not/exist.pdf")
    with pytest.raises(FileNotFoundError):
        parser(file_path=fake_path)


@pytest.mark.integration
def test_parse_document_returns_expected_fields(parsed_result):
    assert isinstance(parsed_result, DocumentSchema)
    assert isinstance(parsed_result.metadata, DocumentMetadata)

    assert set(parsed_result.model_dump().keys()) == {
        "doc_name",
        "raw_text",
        "metadata",
        "binary_hash",
        "chunks",
        "clean_text",
    }


@pytest.mark.integration
def test_parse_document_text_content_is_nonempty_string(parsed_result):
    assert len(parsed_result.raw_text) > 0
    assert isinstance(parsed_result.raw_text, str)


@pytest.mark.integration
def test_parse_document_num_pages_is_positive(parsed_result):
    assert isinstance(parsed_result.metadata.num_pages, int)
    assert parsed_result.metadata.num_pages > 0
