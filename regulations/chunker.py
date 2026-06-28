TR_MAP: ClassVar[dict] = str.maketrans({
    "ç": "c", "Ç": "C",
    "ğ": "g", "Ğ": "G",
    "ı": "i", "İ": "I",
    "ö": "o", "Ö": "O",
    "ş": "s", "Ş": "S",
    "ü": "u", "Ü": "U",
})

@staticmethod
def _add_id(chunks: list[dict]) -> None:
    for chunk in chunks:

        payload = chunk["payload"]

        base_slug = (chunk["payload"]["main_title"]
                     .translate(Parser.TR_MAP)
                     .lower()
                     .replace(" ", "_"))
        base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

        chapter_id = f"chapter_{payload["chapter_number"]:02d}"
        article_id = f"article_{payload["article_number"]:02d}"
        paragraph_id = f"paragraph_{payload["paragraph_number"]:02d}"

        id_items = [base_slug, chapter_id, article_id, paragraph_id]

        if "item_letter" in payload:
            item_id = f"item_{payload["item_letter"]}"
            id_items.append(item_id)

        id_ = ":".join(id_items)

        chunk["payload"]["chunk_id"] = id_
        chunk["point_id"] = str(uuid4())


@staticmethod
def _add_embedding_text(chunks: list[dict]) -> None:
    for chunk in chunks:
        payload = chunk["payload"]
        text = chunk["payload"]["text"]

        parts = [
            f'Belge: {payload["main_title"]}',
            f'Bölüm: {payload["chapter_name"]}',
            f'Madde {payload["article_number"]}: {payload["article_title"]}',
        ]

        if "item_letter" in payload:
            parts.append(f'Paragraf {payload["paragraph_number"]}')
            parts.append(f'Bent {payload["item_letter"]}: {text}')
        else:
            parts.append(f'Paragraf {payload["paragraph_number"]}: {text}')

        embedding_text = "\n".join(parts)

        chunk["embedding_text"] = embedding_text