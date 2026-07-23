from sentence_transformers import SentenceTransformer
from typing import List


def get_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Placeholder: return a SentenceTransformer model instance."""
    raise NotImplementedError


def embed_texts(model: SentenceTransformer, texts: List[str]) -> List[List[float]]:
    """Placeholder: embed texts using the provided model."""
    raise NotImplementedError
