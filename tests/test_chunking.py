import pytest

from src.chunking.fixed_size_chunker import FixedSizeChunker
from src.chunking.recursive_chunker import RecursiveChunker

CHUNK_SIZE = 200
CHUNK_OVERLAP = 50

TEXT = """
Retrieval-Augmented Generation, commonly known as RAG, represents one of the most significant advancements in the field of natural language processing and large language models. At its core, RAG is a framework that enhances the capabilities of generative models by incorporating external knowledge retrieval mechanisms. This approach addresses one of the fundamental limitations of traditional language models: their reliance on static training data and the subsequent inability to access or incorporate information beyond their training cutoff.
"""


@pytest.fixture(params=["fixed", "recursive"])
def chunker(request):
    if request.param == "fixed":
        return FixedSizeChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return RecursiveChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


@pytest.fixture(scope="session")
def fixed_chunker():
    return FixedSizeChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)


def test_empty_string(chunker):
    text = " "
    with pytest.raises(ValueError):
        chunker(text=text)


def test_none_value(chunker):
    text = None
    with pytest.raises(ValueError):
        chunker(text=text)


@pytest.mark.parametrize("chunker_class", [FixedSizeChunker, RecursiveChunker])
def test_invalid_config(chunker_class):
    with pytest.raises(ValueError):
        chunker_class(chunk_size=100, chunk_overlap=200)


def test_output(chunker):
    chunks = chunker(TEXT)
    assert chunks is not None
    assert isinstance(chunks, list)
    assert all([isinstance(chunk, str) for chunk in chunks])
    assert all([len(chunk) <= CHUNK_SIZE for chunk in chunks])


def test_chunking(fixed_chunker):
    chunks = fixed_chunker(text=TEXT)
    idx = 0
    while idx < len(chunks) - 1:
        assert chunks[idx + 1][:CHUNK_OVERLAP] in chunks[idx]
        idx += 1


def test_short_text(chunker):
    text = "Hello"
    chunks = chunker(text=text)
    assert len(chunks) == 1
    assert chunks[0] == "Hello"


def test_charachters_occurance(fixed_chunker):
    chunks = fixed_chunker(TEXT)
    for char in TEXT:
        assert any(char in chunk for chunk in chunks)
