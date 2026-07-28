from src.pdf_reader import read_pdf
from src.chunker import chunk_text
from src.embeddings import generate_embeddings
from src.vector_store import store_embeddings

document_name, pages = read_pdf(
    "Legal_Document_Review_Agent_HybridRAG/data/contracts/nda.pdf"
)

chunks = chunk_text(document_name, pages)

embeddings = generate_embeddings(chunks)

store_embeddings(chunks, embeddings)

from src.retriever import retrieve

from src.context_builder import build_context

retrieved_chunks = retrieve("What is Confidential Information?")

print(retrieved_chunks)

context = build_context(retrieved_chunks)
print("=" * 80)
print(context)
print("=" * 80)

import asyncio

from src.chat import ask_llm

answer = asyncio.run(

    ask_llm(

        "What is Confidential Information?",

        context

    )

)

print(answer)