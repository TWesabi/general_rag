from abc import ABC, abstractmethod
from pathlib import Path

from docling.document_converter import DocumentConverter

from src.utils.logger import setup_logger

log = setup_logger(__name__)


class DocumentParser(ABC):
    @abstractmethod
    def __call__(self, file_path: Path): ...


class PdfParser(DocumentParser):
    def __call__(self, file_path):
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            convertor = DocumentConverter()
            result = convertor.convert(file_path)
        except RuntimeError as e:
            log.error("Something wrong went when parsing the file %s:", file_path, e)
            raise

        doc_data = result.document
        doc_name = doc_data.name
        num_pages = doc_data.num_pages()
        log.info("Docling docuemnt name: %s:", doc_name)
        log.info("Docling docuemnt num pages %s:", num_pages)

        parsed_doc = {
            "local_path": str(file_path),
            "status": result.status,
            "timestamp": result.timestamp,
            "doc_name": doc_name,
            "num_pages": num_pages,
            "text_content": doc_data.export_to_text(),
            "table_count": len(doc_data.tables),
            "has_tables": len(doc_data.tables) > 0,
            "mimetype": doc_data.origin.mimetype,
            "binary_hash": doc_data.origin.binary_hash,
            "filename": doc_data.origin.filename,
        }

        return parsed_doc
