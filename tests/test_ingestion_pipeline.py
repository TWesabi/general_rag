from pathlib import Path

import pytest

from src.db.document_repo import DocumentRepository
from src.db.models import Document
from src.parsers.basic_cleaning import BasicTextCleaner
from src.parsers.parser_pdf import PdfParser
from src.pipelines.ingestion import IngestionPipeline


@pytest.fixture
def parser():
    return PdfParser()


@pytest.fixture
def cleaner():
    return BasicTextCleaner()


@pytest.fixture
def repo(db_session):
    return DocumentRepository(session=db_session)


@pytest.fixture
def create_pipeline(parser, cleaner, repo):
    return IngestionPipeline(pdf_parser=parser, basic_cleaner=cleaner, document_repo=repo)


def test_ingestion_pipeline(create_pipeline):
    result = create_pipeline(Path("tests/data/Test_Sample.pdf"))
    assert isinstance(result, Document)
    assert result.id is not None
    assert isinstance(result.id, int)
    assert result.doc_name is not None
    assert result.status is not None
    assert result.binary_hash is not None
