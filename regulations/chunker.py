from typing import ClassVar
from regulations.chunker_config import ChunkerConfig, ChunkerOption
import re

class Chunker:

    TR_MAP: ClassVar[dict] = str.maketrans({
        "ç": "c", "Ç": "C",
        "ğ": "g", "Ğ": "G",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ş": "s", "Ş": "S",
        "ü": "u", "Ü": "U",
    })

    @staticmethod
    def _create_id(*,
                   main_title: str,
                   chapter_number: int,
                   article_number: int,
                   paragraph_number: int,
                   item_letter: str | None = None,
                   sub_item_number: str | None = None,
                   ) -> str:

        base_slug = (main_title
                     .translate(Chunker.TR_MAP)
                     .lower()
                     .replace(" ", "_"))
        base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

        chapter_id = f"chapter_{chapter_number:02d}"
        article_id = f"article_{article_number:02d}"
        paragraph_id = f"paragraph_{paragraph_number:02d}"

        id_items = [base_slug, chapter_id, article_id, paragraph_id]

        if item_letter:
            item_id = f"item_{item_letter}"
            id_items.append(item_id)

        if sub_item_number:
            sub_item_id = f"sub_item_{sub_item_number:02d}"
            id_items.append(sub_item_id)

        id_ = ":".join(id_items)

        return id_

    @staticmethod
    def _create_embedding_text(payload: dict[str, str | int | None]) -> str:

        parts = [
            f'Belge: {payload["main_title"]}',
            f'Bölüm: {payload["chapter_name"]}',
            f'Madde {payload["article_number"]}: {payload["article_title"]}',
        ]

        text = payload["text"]
        if payload.get("item_letter"):
            if payload.get("sub_")
            parts.append(f'Paragraf {payload["paragraph_number"]}')
            parts.append(f'Bent {payload["item_letter"]}: {text}')
        else:
            parts.append(f'Paragraf {payload["paragraph_number"]}: {text}')

        embedding_text = "\n".join(parts)

        return embedding_text

    @staticmethod
    def _apply_option(option: ChunkerOption,
                      items: list[dict]) -> list[list[dict]]:

        item_merge = option["item_merge"]
        if item_merge == "full":
            return [items]

        elif item_merge == "none":
            return [[i] for i in items]

        else:
            item_group_sizes = option["item_group_sizes"]
            if not item_group_sizes or sum(item_group_sizes) != len(items):
                raise ValueError("Invalid item_group_sizes")

            groups = []
            last = 0
            for idx in item_group_sizes:
                groups.append(items[last:idx])
                last = idx

            return groups

    @staticmethod
    def _create_payload(*,
                      chapter_name: str,
                      chapter_number: int,
                      article_title: str,
                      article_number: int,
                      paragraph_number: int,
                      text: str,
                      item_letter: str | None = None,
                      sub_item_number: int | None = None,
                      ) -> dict[str, str | int | None]:

        payload = {
            "chapter_name": chapter_name,
            "chapter_number": chapter_number,
            "article_title": article_title,
            "article_number": article_number,
            "paragraph_number": paragraph_number,
            "item_letter": item_letter,
            "sub_item_number": sub_item_number,
            "text": text,
        }

        return payload

    @staticmethod
    def _get_chunks(tree: dict, config: ChunkerConfig) -> list[dict]:

        main_title = tree["main_title"]

        for chapter in tree["chapters"]:
            for title in chapter["titles"]:
                for article in title["articles"]:
                    for paragraph in article["paragraphs"]:

                        chapter_number = chapter["chapter_number"]
                        article_number = article["article_number"]
                        paragraph_number = paragraph["paragraph_number"]

                        option = config.get_option(
                            chapter_number=chapter_number,
                            article_number=article_number,
                            paragraph_number=paragraph_number,
                        )
                        items = paragraph["items"]

                        grouped_items = Chunker._apply_option(
                            option=option,
                            items=items
                        )



