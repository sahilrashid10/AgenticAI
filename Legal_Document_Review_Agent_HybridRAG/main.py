from src.pdf_reader import read_pdf
from src.chunker import chunk_text
from src.embeddings import generate_embeddings
from src.vector_store import store_embeddings
from src.retriever import hybrid_retrieve
from src.context_builder import build_context
from src.chat import ask_llm

import os
import asyncio

pdf_folder = "Legal_Document_Review_Agent_HybridRAG/data/contracts"

all_chunks = []

for filename in os.listdir(pdf_folder):

    if filename.endswith(".pdf"):

        pdf_path = os.path.join(pdf_folder, filename)

        document_name, pages = read_pdf(pdf_path)

        chunks = chunk_text(document_name, pages)

        all_chunks.extend(chunks)

        embeddings = generate_embeddings(chunks)

        store_embeddings(chunks, embeddings)

question = "What is Confidential Information?"

retrieved_chunks = hybrid_retrieve(
    question,
    all_chunks,
    top_k=3
)

context = build_context(retrieved_chunks)

print("=" * 80)
print(context)
print("=" * 80)

answer = asyncio.run(
    ask_llm(
        question,
        context
    )
)

print(answer)