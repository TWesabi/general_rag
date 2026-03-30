from src.db.chunck_repo import ChunkRepository
from src.storage.vector_store import VectorStore
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class IndexingPipeline:
    def __init__(self, vector_store: VectorStore, chunk_repo: ChunkRepository):
        self.vector_store = vector_store
        self.chunk_repo = chunk_repo

    def __call__(self, document_id: int | None = None) -> None:
        if document_id:
            chunks = self.chunk_repo.get_by_document_id(document_id)
        else:
            chunks = self.chunk_repo.get_all()
        self.vector_store.create_collection()
        self.vector_store.add(chunks=chunks)
        log.info("Indexed %s chunks", len(chunks))
