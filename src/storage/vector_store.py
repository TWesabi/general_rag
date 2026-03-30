from abc import ABC, abstractmethod

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    ScoredPoint,
    VectorParams,
)

from src.config import settings
from src.db.models import Chunk
from src.embeddings.embedding import BaseEmbedder
from src.schemas.query import QdrantFilterSchema, RetrievalResult
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class VectorStore(ABC):

    @abstractmethod
    def __init__(self, embedder: BaseEmbedder):
        self.embedder = embedder

    @abstractmethod
    def create_collection(self, name: str = None) -> None: ...
    @abstractmethod
    def add(self, chunks: list[Chunk]) -> None: ...
    @abstractmethod
    def search(
        self, user_query: str, top_k: int, query_filter: dict | None = None
    ) -> list[RetrievalResult]: ...


class QdrantVectorStore(VectorStore):
    def __init__(self, embedder: BaseEmbedder):
        self.client = QdrantClient(url=settings.QDRANT__URL)
        self.collection_name = settings.QDRANT__COLLECTION_NAME
        self.embedder = embedder

    def create_collection(self, name: str = None):

        if name:
            self.collection_name = name

        if self.client.collection_exists(collection_name=self.collection_name):
            log.info("Collection %s already exists!", self.collection_name)
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=settings.QDRANT__VECTOR_SIZE, distance=Distance.COSINE
            ),
        )
        log.info("Collection %s created successfully!", self.collection_name)

    def add(self, chunks: list[Chunk]):
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                wait=True,
                points=self._chunks_to_points(chunks),
            )
            log.info(
                "All %s Chunks are inserted successfully into %s Collection!",
                len(chunks),
                self.collection_name,
            )
        except ConnectionError:
            log.error("Qdrant is not reachable!")
            raise

    def _chunks_to_points(self, chunks: list[Chunk]) -> list[PointStruct]:
        all_chunks = [chunk.content for chunk in chunks]
        all_embeddings = self.embedder(all_chunks)
        points = []
        for chunk, embedding in zip(chunks, all_embeddings):
            metadata = {
                "document_id": chunk.document_id,
                "position": chunk.position,
                "hints": chunk.hints,
                "has_table": chunk.has_table,
                "has_image": chunk.has_image,
                "created_at": str(chunk.created_at),
                "content": chunk.content,
            }
            points.append(PointStruct(id=chunk.id, vector=embedding, payload=metadata))
        return points

    def search(
        self, user_query, top_k=settings.TOP_K, query_filter: QdrantFilterSchema | None = None
    ) -> list[RetrievalResult]:

        if query_filter:
            query_filter = self._create_filter_from_schema(query_filter)

        query_vector = self.embedder([user_query])[0]
        search_result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            with_payload=True,
            limit=top_k,
        ).points

        retrieval_result = self._to_retrieval_results(search_result)

        return retrieval_result

    def get_all(self) -> list[PointStruct]:
        all_points = []
        offset = None

        while True:
            points, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=settings.QDRANT__SCROLL_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )

            all_points.extend(points)

            if offset is None:
                break
        log.info("All %s documents in Vector Store are retrieved!", len(all_points))

        return all_points

    def _create_filter_from_schema(self, filter_schema: QdrantFilterSchema) -> Filter:
        filters = Filter(
            must=(
                [
                    FieldCondition(key=key, match=MatchValue(value=filter_schema.musts[key]))
                    for key in filter_schema.musts
                ]
                if filter_schema.musts
                else None
            ),
            should=(
                [
                    FieldCondition(key=key, match=MatchValue(value=filter_schema.shoulds[key]))
                    for key in filter_schema.shoulds
                ]
                if filter_schema.shoulds
                else None
            ),
            must_not=(
                [
                    FieldCondition(key=key, match=MatchValue(value=filter_schema.must_nots[key]))
                    for key in filter_schema.must_nots
                ]
                if filter_schema.must_nots
                else None
            ),
        )
        return filters

    def _to_retrieval_results(self, scored_points: list[ScoredPoint]) -> list[RetrievalResult]:
        retrieval_result: list[RetrievalResult] = []
        for point in scored_points:
            result = RetrievalResult(
                content=point.payload.get("content"),
                score=point.score,
                document_id=point.payload.get("document_id"),
                position=point.payload.get("position"),
                hints=point.payload.get("hints"),
            )
            retrieval_result.append(result)
        return retrieval_result

    ##TODO: Delete Collection
