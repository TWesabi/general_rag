from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.database import get_session
from src.db.document_repo import DocumentRepository
from src.db.models import Document


@pytest.fixture
def document_repo():
    session = get_session()
    doc_repo = DocumentRepository(session=session)
    yield doc_repo
    session.rollback()
    session.close()


@pytest.mark.integration
def test_insert_document(document_repo):
    doc = Document(doc_name="Test_Doc", binary_hash="1234abc", status="cleaned")
    document_repo.add(doc=doc)
    assert doc.doc_name == "Test_Doc"
    assert doc.binary_hash == "1234abc"
    assert doc.status == "cleaned"
    assert isinstance(doc.id, int)
    assert isinstance(doc.created_at, datetime)


@pytest.mark.integration
def test_binary_hash_constraint(document_repo):
    doc_1 = Document(doc_name="Test_Doc", binary_hash="1234abc", status="cleaned")
    doc_2 = Document(doc_name="Test_Doc_2", binary_hash="1234abc", status="cleaned")
    document_repo.add(doc_1)
    with pytest.raises(IntegrityError):
        document_repo.add(doc_2)


@pytest.mark.integration
def test_get_by_hash_notfound(document_repo):
    doc_1 = Document(doc_name="Test_Doc", binary_hash="1234abc", status="cleaned")
    document_repo.add(doc_1)
    doc = document_repo.get_by_hash(binary_hash="123654")
    assert doc is None


@pytest.mark.integration
def test_get_by_id(document_repo):
    doc_1 = Document(doc_name="Test_Doc", binary_hash="1234abc", status="cleaned")
    document_repo.add(doc=doc_1)
    retrieved = document_repo.get_by_id(doc_1.id)
    assert retrieved.doc_name == "Test_Doc"
    assert retrieved.binary_hash == "1234abc"
    assert retrieved.status == "cleaned"
    assert isinstance(retrieved.id, int)
    assert isinstance(retrieved.created_at, datetime)


@pytest.mark.integration
def test_delete_document(document_repo):
    doc_1 = Document(doc_name="Test_Doc", binary_hash="1234abc", status="cleaned")
    document_repo.add(doc=doc_1)
    document_repo.delete(doc_1.id)
    retrieved = document_repo.get_by_id(doc_1.id)
    assert retrieved is None
