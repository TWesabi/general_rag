from abc import ABC, abstractmethod

from src.config import settings
from src.schemas.query import QdrantFilterSchema, RetrievalResult
from src.storage.vector_store import VectorStore
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class BaseRetriever(ABC):

    @abstractmethod
    def __init__(self):
        """Initializes the retriever with a Vector Store that performs the retirving"""
        ...

    @abstractmethod
    def __call__(
        self, user_query: str, top_k: int = settings.TOP_K, filters: dict = None
    ) -> list[RetrievalResult] | None:
        """Performs the retrieval, takes a query, top-k, filters and gives a list of Retrieval result"""
        ...


class QdrantRetriever(BaseRetriever):

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def __call__(
        self, user_query: str, top_k: int = settings.TOP_K, filters: QdrantFilterSchema = None
    ) -> list[RetrievalResult] | None:
        result = self.vector_store.search(user_query=user_query, query_filter=filters)
        return result
