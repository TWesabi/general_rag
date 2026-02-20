"""Tests for chunking."""

import pytest

from rag_system.chunking import Chunker, ChunkingStrategy
from rag_system.models.document import Document, DocumentMetadata


@pytest.fixture
def sample_document():
    """Create sample document."""
    metadata = DocumentMetadata(
        source="test.pdf",
        file_type="pdf",
    )
    return Document(
        content="This is a test document. " * 100,  # Create a longer document
        metadata=metadata,
    )


@pytest.fixture
def chunker():
    """Create chunker instance."""
    return Chunker(chunk_size=100, chunk_overlap=10)


def test_chunker_initialization(chunker):
    """Test chunker initialization."""
    assert chunker.chunk_size == 100
    assert chunker.chunk_overlap == 10
    assert chunker.strategy == ChunkingStrategy.RECURSIVE


def test_chunk_document(chunker, sample_document):
    """Test document chunking."""
    chunks = chunker.chunk_document(sample_document)
    assert len(chunks) > 0
    assert all(chunk.content for chunk in chunks)
    assert all(chunk.chunk_index >= 0 for chunk in chunks)


def test_chunk_overlap(chunker, sample_document):
    """Test that chunks have overlap."""
    chunks = chunker.chunk_document(sample_document)
    if len(chunks) > 1:
        # Check that consecutive chunks overlap
        first_end = chunks[0].end_char
        second_start = chunks[1].start_char
        assert first_end > second_start
