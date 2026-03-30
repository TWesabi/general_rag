from src.embeddings.embedding import OllamaEmbedder
from src.retrieval.retriever import QdrantRetriever
from src.storage.vector_store import QdrantVectorStore
from src.utils.logger import setup_logger

log = setup_logger(__name__)

embedder = OllamaEmbedder()
v_store = QdrantVectorStore(embedder=embedder)
retriever = QdrantRetriever(vector_store=v_store)

quey = "What is RAG?"

results = retriever(user_query=quey, top_k=3)

log.info(f"Results: {results}")
