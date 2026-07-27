from bisect import bisect_right

from src.models import Chunk


def get_page_number(character_position, page_starts, page_boundaries):

    index = bisect_right(page_starts, character_position) - 1

    return page_boundaries[index]["page"]


def chunk_text(document_name, pages, chunk_size=500, overlap=100):
        if overlap >= chunk_size:
            raise ValueError("Overlap must be smaller than chunk size.")

        full_text = ""

        page_boundaries = []

        page_starts = []

        for page in pages:

            page_boundaries.append({
                "page": page.page,
                "start": len(full_text)
            })

            page_starts.append(len(full_text))

            full_text += page.text + "\n"

        print(page_boundaries)
        print(page_starts)
        print(len(full_text))
        print(get_page_number(3500, page_starts, page_boundaries))
        print(get_page_number(7200, page_starts, page_boundaries))
        chunks = []

        step_size = chunk_size - overlap

        for start_char in range(0, len(full_text), step_size):

            end_char = min(start_char + chunk_size, len(full_text))

            chunk_text = full_text[start_char:end_char]

            start_page = get_page_number(
                start_char,
                page_starts,
                page_boundaries
            )

            end_page = get_page_number(
                end_char - 1,
                page_starts,
                page_boundaries
            )

            chunks.append(

                Chunk(

                    id=f"{document_name}_chunk_{len(chunks)}",

                    document=document_name,

                    text=chunk_text,

                    start_char=start_char,

                    end_char=end_char,

                    start_page=start_page,

                    end_page=end_page

                )

            )

        return chunks
