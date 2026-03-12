from pathlib import Path

from src.db.document_repo import DocumentRepository
from src.db.models import Document
from src.parsers.basic_cleaning import BasicTextCleaner
from src.parsers.parser_pdf import PdfParser


class IngestionPipeline:
    def __init__(
        self,
        pdf_parser: PdfParser,
        basic_cleaner: BasicTextCleaner,
        document_repo: DocumentRepository,
    ):
        self.document_repo = document_repo
        self.basic_cleaner = basic_cleaner
        self.pdf_parser = pdf_parser

    def __call__(self, path: Path) -> Document:
        parsed_doc = self.pdf_parser(file_path=path)
        doc = self._document_builder(parsed_doc=parsed_doc)
        clean_text = self.basic_cleaner(doc.raw_text)
        doc.clean_text = clean_text
        db_doc = self._map_to_document_model(doc)
        written_doc = self.document_repo.add(db_doc)
        return written_doc
