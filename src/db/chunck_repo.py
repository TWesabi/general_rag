from sqlalchemy.orm import Session

from src.db.models import Chunk


class ChunkRepository:

    def __init__(self, session: Session):
        self._session = session

    def add(self, chunk: Chunk) -> Chunk:
        """Adds a chunck to the database and returns the Chunk if succeeded and raises if fails"""
        ...

    def get_by_id(self, id: int) -> Chunk:
        """Fetches a chunck by its ID and returns the Chunk"""
        ...

    def get_by_document_id(self, doc_id: int) -> list[Chunk]:
        """Given a document ID as foreign key, returns all chuncks of that document"""
        ...

    def get_all(self) -> list[Chunk]:
        """Returns all chuncks in the database grouped by document"""
        ...

    def delete(self, id: int) -> None:
        """Deletes a given chunck by its ID and returns nothing if succeeded and raises if fails"""
        ...
