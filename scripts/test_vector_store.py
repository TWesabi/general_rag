from src.db.models import Chunk
from src.embeddings.embedding import OllamaEmbedder
from src.storage.vector_store import QdrantVectorStore

embedder = OllamaEmbedder()

store = QdrantVectorStore(embedder=embedder)

store.create_collection()

points = store.get_all()

# question = "What is RAG?"

# answers = store.search(user_query=question, top_k=5)

# texts = [answer.payload["content"] for answer in answers]

# print(type(texts))
# print(texts)

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


# store.add(ml_chunks)
