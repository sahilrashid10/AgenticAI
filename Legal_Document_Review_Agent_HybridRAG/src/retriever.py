import chromadb
from sentence_transformers import SentenceTransformer
from src.models import Chunk

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection("legal-documents")


def retrieve(query, top_k=3):

    query_embedding = model.encode(query)

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    retrieved_chunks = []

    for i in range(len(results["ids"][0])):

        metadata = results["metadatas"][0][i]

        retrieved_chunks.append(

            Chunk(

                id=results["ids"][0][i],

                document=metadata["document"],

                text=results["documents"][0][i],

                start_char=metadata["start_char"],

                end_char=metadata["end_char"],

                start_page=metadata["start_page"],

                end_page=metadata["end_page"]

            )

        )

    return retrieved_chunks


STOP_WORDS = {
    "what",
    "is",
    "the",
    "a",
    "an",
    "of",
    "to",
    "in",
    "for",
    "and",
    "does",
    "do",
    "are",
    "can"
}

def keyword_search(query, chunks, top_k=3):

    keywords = [
        word
        for word in query.lower().split()
        if word not in STOP_WORDS
    ]

    results = []

    for chunk in chunks:

        score = 0
        text = chunk.text.lower()

        for word in keywords:
            if word in text:
                score += 1

        if score > 0:
            results.append((score, chunk))

    results.sort(key=lambda x: x[0], reverse=True)

    return [chunk for score, chunk in results[:top_k]]
def hybrid_retrieve(query, chunks, top_k=3):

    vector_results = retrieve(query, top_k)
    keyword_results = keyword_search(query, chunks, top_k)

    merged = {}

    for chunk in vector_results + keyword_results:
        merged[chunk.id] = chunk

    return list(merged.values())