import pytest

from src.db.models import Chunk
from src.embeddings.embedding import OllamaEmbedder
from src.schemas.query import QdrantFilterSchema
from src.storage.vector_store import QdrantVectorStore

ml_chunks = [
    Chunk(
        id=1,
        document_id=1,
        position=0,
        content="Machine learning uses data to train models that make predictions.",
    ),
    Chunk(
        id=2,
        document_id=1,
        position=1,
        content="A neural network has multiple layers of nodes that process input signals.",
    ),
    Chunk(
        id=3,
        document_id=1,
        position=2,
        content="Gradient descent finds the minimum of a loss function by updating weights.",
    ),
]

cooking_chunks = [
    Chunk(
        id=4,
        document_id=2,
        position=0,
        content="Sauteing uses a small amount of oil in a hot pan to cook food quickly.",
    ),
    Chunk(
        id=5,
        document_id=2,
        position=1,
        content="Braising combines high heat searing with slow cooking in a covered pot.",
    ),
    Chunk(
        id=6,
        document_id=2,
        position=2,
        content="Emulsification blends oil and water into a stable mixture using an emulsifier.",
    ),
]

mixed_chunks = [
    Chunk(
        id=1,
        document_id=2,
        position=0,
        content="Sauteing uses a small amount of oil in a hot pan to cook food quickly.",
    ),
    Chunk(
        id=2,
        document_id=1,
        position=0,
        content="Machine learning uses data to train models that make predictions.",
    ),
]


@pytest.fixture(scope="module")
def test_vector_store():
    embedder = OllamaEmbedder()
    store = QdrantVectorStore(embedder=embedder)
    store.create_collection(name="test_collection")
    yield store
    store.client.delete_collection(collection_name="test_collection")


@pytest.mark.integration
def test_add_chunks(test_vector_store):
    v_store = test_vector_store
    v_store.add(chunks=ml_chunks)
    all_chunks = v_store.get_all()
    assert len(all_chunks) == len(ml_chunks)


@pytest.mark.integration
def test_search_chunks(test_vector_store):
    v_store = test_vector_store
    v_store.add(chunks=ml_chunks)
    result = v_store.search(user_query="Gradient descent ")
    assert result != []
    assert isinstance(result, list)
    assert all([item.score is not None for item in result])


@pytest.mark.integration
def test_relevance(test_vector_store):
    v_store = test_vector_store
    v_store.add(chunks=mixed_chunks)
    result = v_store.search(user_query="Machine learning")
    assert result[0].content == mixed_chunks[1].content


@pytest.mark.integration
def test_metadata_filter(test_vector_store):
    v_store = test_vector_store
    v_store.add(chunks=ml_chunks)
    v_store.add(chunks=cooking_chunks)
    filtering = QdrantFilterSchema(musts={"document_id": 1})
    result = v_store.search(user_query="Gradient descent", query_filter=filtering)
    assert all([point.document_id == 1 for point in result])
