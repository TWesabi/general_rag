from pathlib import Path

from src.db.document_repo import DocumentRepository
from src.db.models import Document
from src.parsers.basic_cleaning import TextCleaner
from src.parsers.parser_pdf import DocumentParser
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        pdf_parser: DocumentParser,
        basic_cleaner: TextCleaner,
        document_repo: DocumentRepository,
    ):
        self.document_repo = document_repo
        self.basic_cleaner = basic_cleaner
        self.pdf_parser = pdf_parser

    def __call__(self, path: Path) -> Document:
        log.info("Starting ingestion for %s", path)
        parsed_doc = self.pdf_parser(file_path=path)
        log.info("Parsed %s — %s pages", parsed_doc.doc_name, parsed_doc.metadata.num_pages)
        parsed_doc.clean_text = self.basic_cleaner(parsed_doc.raw_text)
        log.info("Text cleaned for %s", parsed_doc.doc_name)
        db_doc = self.document_repo.from_schema(parsed_doc)
        written_doc = self.document_repo.add(db_doc)
        log.info(
            "Ingestion complete for %s — stored with id %s", written_doc.doc_name, written_doc.id
        )
        return written_doc
