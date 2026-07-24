from src.pdf_reader import read_pdf

text = read_pdf("Legal_Document_Review_Agent_HybridRAG/data/contracts/nda.pdf")

print(text[:1000])