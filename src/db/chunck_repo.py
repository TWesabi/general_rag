from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.db.models import Chunk
from src.schemas.document import ChunkSchema
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class ChunkRepository:

    def __init__(self, session: Session):
        self._session = session

    def add(self, chunk: Chunk) -> Chunk:
        """Adds a chunck to the database and returns the Chunk if succeeded and raises if fails"""
        try:
            self._session.add(chunk)
            self._session.flush()
            log.info("Chunk added successfully! to Document %s", chunk.document_id)
            return chunk
        except (OperationalError, IntegrityError) as e:
            log.error("Chunk in document %s could not be added. Error is: %s", chunk.document_id, e)
            raise

    def add_batch(self, chunks: list[Chunk]) -> list[Chunk]:
        """Adds multiple chunks to the database."""
        try:
            self._session.add_all(chunks)
            self._session.flush()
            log.info("Added %s chunks", len(chunks))
            return chunks
        except (OperationalError, IntegrityError) as e:
            log.error("Chunks in document could not be added. Error is: %s", e)
            raise

    def get_by_id(self, id: int) -> Chunk:
        """Fetches a chunck by its ID and returns the Chunk"""
        ...

    def get_by_document_id(self, doc_id: int) -> list[Chunk]:
        """Given a document ID as foreign key, returns all chuncks of that document"""
        chuncks = self._session.query(Chunk).filter(Chunk.document_id == doc_id).all()
        if not chuncks:
            log.warning("There is not chunck with document_id: %s", doc_id)
            return chuncks

        log.info("Chunks fetched successfully")
        return chuncks

    def get_all(self) -> list[Chunk]:
        """Returns all chuncks in the database grouped by document"""
        chunks = self._session.query(Chunk).all()
        log.info("All elements of type Chunk fetched successfully")
        return chunks

    def delete(self, id: int) -> None:
        """Deletes a given chunck by its ID and returns nothing if succeeded and raises if fails"""
        ...

    def from_chunks_schema(self, chunk_schemas: list[ChunkSchema], document_id: int) -> list[Chunk]:
        chunks: list[Chunk] = []
        for chunk_schema in chunk_schemas:
            chunk = Chunk(
                document_id=document_id,
                position=chunk_schema.position,
                hints=chunk_schema.hints,
                content=chunk_schema.content,
                has_table=chunk_schema.has_table,
                has_image=chunk_schema.has_image,
            )
            chunks.append(chunk)
        return chunks
