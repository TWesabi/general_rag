from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from src.db.models import Document, DocumentStatus
from src.schemas.document import DocumentSchema
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class DocumentRepository:

    def __init__(self, session: Session):
        self._session = session

    def add(self, doc: Document | DocumentSchema) -> Document:
        """Adds a document to the database and returns the Document if succeeded and raises if fails"""
        if doc is DocumentSchema:
            doc = self._from_schema(doc)
            log.info("Converting Document %s from schema!", doc.filename)

        try:
            self._session.add(doc)
            self._session.flush()
            log.info(
                "Document with binary_hash %s added successfully and has id %s: ",
                doc.binary_hash,
                doc.id,
            )
            return doc

        except (OperationalError, IntegrityError) as e:
            log.error("Document %s could not be added. Error is: %s", doc.filename, e)
            raise

    def get_by_id(self, id: int) -> Document | None:
        """Fetches a document by its ID and returns the Document"""

        doc = self._session.query(Document).filter(Document.id == id).first()
        if doc is None:
            log.warning("There is not document with id: %s", id)
            return doc
        log.info("Document %s fetched successfully", doc.id)
        return doc

    def get_by_hash(self, binary_hash: str) -> Document | None:
        """Fetches a document, given a binary hash and returns this Document or nothing if no document exist"""

        doc = self._session.query(Document).filter(Document.binary_hash == binary_hash).first()
        if doc is None:
            log.warning("There is not document with binary_hash: %s", binary_hash)
            return doc
        log.info("Document %s fetched successfully", doc.id)
        return doc

    def get_all(self) -> list[Document]:
        """Returns all documents in the database"""

        docs = self._session.query(Document).all()
        log.info("All elements of type Document fetched successfully")
        return docs

    def delete(self, id: int) -> None:
        """Deletes a given document by its ID and returns nothing if succeeded and raises if fails"""
        self._session.query(Document).filter(Document.id == id).delete()
        self._session.flush()
        log.info("Document %s deleted successfully!", id)

    def update_status(self, doc: Document, status: DocumentStatus) -> Document:
        """Updates the status of the document based on its stage in the pipeline and returns the updated Document"""

        doc.status = status
        self._session.flush()
        log.info("Document %s status updated to %s successfully!", doc.id, status)
        return doc

    def _from_schema(self, schema: DocumentSchema) -> Document:

        db_doc = Document(
            doc_name=schema.doc_name,
            filename=schema.metadata.filename,
            binary_hash=schema.binary_hash,
            mimetype=schema.metadata.mimetype,
            local_path=schema.metadata.local_path,
            num_pages=schema.metadata.num_pages,
            status=schema.metadata.status,
        )

        return db_doc
