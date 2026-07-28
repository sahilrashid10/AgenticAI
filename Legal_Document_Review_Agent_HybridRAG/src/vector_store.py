import chromadb

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="legal-documents"
)


def store_embeddings(chunks, embeddings):

    ids = []

    documents = []

    metadatas = []

    for chunk in chunks:

        ids.append(chunk.id)

        documents.append(chunk.text)

        metadatas.append({

            "document": chunk.document,

            "start_page": chunk.start_page,

            "end_page": chunk.end_page,

            "start_char": chunk.start_char,

            "end_char": chunk.end_char

        })

    collection.upsert(

        ids=ids,

        documents=documents,

        embeddings=embeddings.tolist(),

        metadatas=metadatas

    )