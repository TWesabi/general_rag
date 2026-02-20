from docling.document_converter import DocumentConverter, PdfFormatOption

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, EasyOcrOptions

source = "D:\\Entwicklungsprojekte\\local-chatbot\\rag_system\\docs\\to_index\\agentic_paper.pdf"
artifacts_path = "C:\\Users\\talwesabi\\.cache\\docling\\models\\"
# convertor = DocumentConverter()
# doc = convertor.convert(source)
# print(doc)

pipeline_options = PdfPipelineOptions(artifacts_path=artifacts_path)
doc_converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

doc = doc_converter.convert(source)
print(doc)
