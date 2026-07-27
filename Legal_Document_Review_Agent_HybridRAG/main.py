from src.pdf_reader import read_pdf
from src.chunker import chunk_text

document_name, pages = read_pdf(
    "Legal_Document_Review_Agent_HybridRAG/data/contracts/nda.pdf"
)

chunk_text(document_name, pages)