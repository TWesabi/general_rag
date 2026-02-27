from pathlib import Path

from docling.document_converter import DocumentConverter

from src.utils.logger import setup_logger

log = setup_logger(__name__)


def parse_document(file_path: Path):
    convertor = DocumentConverter()
    result = convertor.convert(file_path)
    # log.info("Docling's result type: %s", {type(result)})  ## formating strings for logging is different from normal f-strings
    # log.info(f"Docling's result attributs: {dir(result)}")
    log.info("Docling's result status: %s", {result.status})
    doc = result.document
    log.info("Docling docuemnt type: %s", {type(doc)})
    log.info(f"Docling docuemnt attributs : {dir(doc)}")
    log.info(f"Docling docuemnt name : {doc.name}")
    # log.info(f"Docling docuemnt number of pages : {doc.num_pages}")
    log.info(f"Docling docuemnt origin : {doc.origin}")
    log.info(f"Docling docuemnt export as text : {doc.export_to_text()[:100]}")
    log.info(f"Docling docuemnt export as markdown : {doc.export_to_markdown()[:100]}")
    # log.info(f"Docling docuemnt texts : {doc.texts}")
    log.info(f"Docling docuemnt pages : {doc.pages}")
    return result


if __name__ == "__main__":
    pdf_path = Path("docs\\to_index\\Test_Text.pdf")
    result = parse_document(pdf_path)
