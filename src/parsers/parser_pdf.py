from abc import ABC, abstractmethod
from pathlib import Path

from docling.document_converter import DocumentConverter

from src.schemas.document import DocumentMetadata, DocumentSchema, DocumentStatus
from src.utils.logger import setup_logger

log = setup_logger(__name__)


class DocumentParser(ABC):
    @abstractmethod
    def __call__(self, file_path): ...


class PdfParser(DocumentParser):
    def __call__(self, file_path: Path) -> DocumentSchema:
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            convertor = DocumentConverter()
            result = convertor.convert(file_path)
        except RuntimeError as e:
            log.error("Failed to parse file %s: %s", file_path, e)
            raise

        doc_data = result.document
        doc_name = doc_data.name
        num_pages = doc_data.num_pages()
        log.info("Docling docuemnt name: %s:", doc_name)
        log.info("Docling docuemnt num pages %s:", num_pages)

        doc_metadata = DocumentMetadata(
            local_path=str(file_path),
            status=DocumentStatus.PARSED,
            timestamp=result.timestamp,
            num_pages=num_pages,
            table_count=len(doc_data.tables),
            has_tables=len(doc_data.tables) > 0,
            filename=doc_data.origin.filename,
            mimetype=doc_data.origin.mimetype,
        )
        parsed_doc = DocumentSchema(
            doc_name=doc_name,
            raw_text=doc_data.export_to_text(),
            metadata=doc_metadata,
            binary_hash=str(doc_data.origin.binary_hash),
            chunks=None,
            clean_text=None,
        )

        return parsed_doc
