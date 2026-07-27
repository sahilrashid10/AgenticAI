from src.models import Chunk


def chunk_text(document_name, pages, chunk_size=500, overlap=100):

    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    full_text = ""
    page_boundaries = []

    for page in pages:

        page_boundaries.append({
            "page": page.page,
            "start": len(full_text)
        })

        full_text += page.text + "\n"

    print(page_boundaries)
    print(f"Total Characters: {len(full_text)}")