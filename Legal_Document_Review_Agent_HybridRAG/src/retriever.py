import chromadb
from src.models import Chunk
from sentence_transformers import SentenceTransformer

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