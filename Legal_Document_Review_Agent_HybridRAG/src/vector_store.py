import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="legal-documents"
)


def store_embeddings(chunks, embeddings):

    ids = []

    metadata = []

    for i in range(len(chunks)):
        ids.append(f"chunk_{i}")

        metadata.append({
            "source": "nda.pdf",
            "chunk_number": i
        })

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=metadata
    )