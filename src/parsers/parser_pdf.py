from pathlib import Path
from typing import Any

from docling.document_converter import DocumentConverter

from src.utils.logger import setup_logger

log = setup_logger(__name__)


def parse_document(file_path: Path) -> dict[str, Any]:

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


# def handle_tables(raw_text: str) -> str:
#     check if there are table
#     identify them with some character or form
#     strip these vertical lines and dashes that form the table in md
#     gather the content of the cells and label them accoring to theri conext, header of colluns or row etc to maintain context
#     then get back the labeled text as a chunk


if __name__ == "__main__":
    pdf_path = Path("docs\\to_index\\Test_Table_Image.pdf")
    clean_output_path = Path("docs\\to_index\\Test_Table_Image_clean.txt")
    output_path = Path("docs\\to_index\\Test_Table_Image.txt")
    output_dict = parse_document(pdf_path)
