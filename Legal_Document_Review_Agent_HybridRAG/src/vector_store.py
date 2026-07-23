import chromadb
from typing import List, Optional


def create_chroma_client(path: str = "chroma_db") -> chromadb.PersistentClient:
    """Placeholder: create and return a ChromaDB client pointing at `path`."""
    raise NotImplementedError


def upsert_documents(client, collection_name: str, ids: List[str], documents: List[str], embeddings: List[List[float]]):
    """Placeholder: upsert documents into a ChromaDB collection."""
    raise NotImplementedError
