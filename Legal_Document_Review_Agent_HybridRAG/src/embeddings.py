from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embeddings(chunks):

    if not chunks:
        raise ValueError("No chunks were provided for embedding.")

    texts = [chunk.text for chunk in chunks]

    embeddings = model.encode(texts)

    return embeddings