def build_context(chunks):

    context_parts = []

    for chunk in chunks:

        context_parts.append(

            f"""Document: {chunk.document}
Pages: {chunk.start_page}-{chunk.end_page}

{chunk.text}"""

        )

    return "\n\n-------------------------\n\n".join(context_parts)