import os
import fitz

from src.models import Page


def read_pdf(file_path):

    document = fitz.open(file_path)

    pages = []

    document_name = os.path.basename(file_path)

    for page_number, page in enumerate(document, start=1):

        pages.append(
            Page(
                page=page_number,
                text=page.get_text()
            )
        )

    document.close()

    return document_name, pages

