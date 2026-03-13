import pytest

from src.chunking.fixed_size_chunker import FixedSizeChunker
from src.chunking.recursive_chunker import RecursiveChunker

CHUNK_SIZE = 200
CHNK_OVERLAP = 50

TEXT = """
Chapter 1: The Foundations of RAG

The Problem with Traditional Language Models

Traditional language models, including early transformer-based architectures, operate purely on the knowledge they acquired during training.
"""


@pytest.fixture(params=["fixed", "recursive"])
def chunker(request):
    if request.param == "fixed":
        return FixedSizeChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHNK_OVERLAP)
    return RecursiveChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHNK_OVERLAP)


def test_empty_string(chunker):
    text = " "
    with pytest.raises(ValueError):
        chunker(text=text)


def test_output_type(chunker):
    chunks = chunker(TEXT)
    assert chunks is not None
    assert isinstance(chunks, list)
    assert all([isinstance(chunk, str) for chunk in chunks])
    assert all([len(chunk) <= CHUNK_SIZE for chunk in chunks])
