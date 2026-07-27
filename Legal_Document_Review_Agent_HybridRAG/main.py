from src.pdf_reader import read_pdf
from src.chunker import chunk_text
from src.embeddings import generate_embeddings

document_name, pages = read_pdf(
    "Legal_Document_Review_Agent_HybridRAG/data/contracts/nda.pdf"
)

chunks = chunk_text(document_name, pages)

embeddings = generate_embeddings(chunks)

print(f"Chunks: {len(chunks)}")
print(f"Embeddings: {len(embeddings)}")
print(f"Dimensions: {len(embeddings[0])}")