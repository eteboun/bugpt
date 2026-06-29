import uuid
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
    def _create_id(payload: dict[str, str | int | list[dict]]) -> str:

        base_slug = (payload["main_title"]
                     .translate(Chunker.TR_MAP)
                     .lower()
                     .replace(" ", "_"))
        base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

        chapter_id = f"chapter_{payload["chapter_number"]:02d}"
        article_id = f"article_{payload["article_number"]:02d}"
        paragraph_id = f"paragraph_{payload["paragraph_number"]:02d}"

        id_items = [base_slug, chapter_id, article_id, paragraph_id]

        if payload["items_included"]:
            items = payload["items_included"]
            item_ids = []
            for item in items:
                item_letter = item["item_letter"]
                sub_item_number = item["sub_item_number"]

                item_id = f"{item_letter}_{sub_item_number}"\
                    if sub_item_number\
                    else item_letter
                item_ids.append(item_id)

            final_item_id = f"items_{"_".join(item_ids)}"
            id_items.append(final_item_id)

        id_ = ":".join(id_items)

        return id_

    @staticmethod
    def _create_embedding_text(payload: dict[str, str | int | list[dict]]) -> str:

        parts = [
            f'Belge: {payload["main_title"]}',
            f'Bölüm: {payload["chapter_name"]}',
            f'Madde {payload["article_number"]}: {payload["article_title"]}',
        ]

        text = payload["text"]

        items_included = payload["items_included"]
        if items_included:
            parts.append(f'Paragraf {payload["paragraph_number"]}')
            item_displays = []

            for item in items_included:
                item_letter = item["item_letter"]
                sub_item_number = item["sub_item_number"]

                item_display = f"{item_letter}.{sub_item_number}" if sub_item_number else item_letter
                item_displays.append(item_display)

            display_text = f"Bentler {", ".join(item_displays)}: {text}"
            parts.append(display_text)
        else:
            parts.append(f'Paragraf {payload["paragraph_number"]}: {text}')

        embedding_text = "\n".join(parts)

        return embedding_text

    @staticmethod
    def _create_grouped_items(
            option: ChunkerOption,
            items: list[dict],
    ) -> list[list[dict]]:

        item_merge = option["item_merge"]

        if item_merge == "full":
            return [items]

        if item_merge == "none":
            return [[item] for item in items]

        item_group_sizes = option["item_group_sizes"]

        if not item_group_sizes or sum(item_group_sizes) != len(items):
            raise ValueError("Invalid item_group_sizes")

        groups: list[list[dict]] = []
        last = 0

        for size in item_group_sizes:
            end = last + size
            groups.append(items[last:end])
            last = end

        return groups

    @staticmethod
    def _create_payloads_by_paragraph(option: ChunkerOption,
                                   paragraph: dict) -> list[dict[str, str | int | list[dict]]]:

        payloads = []
        include_paragraph_content = option["include_paragraph_content"]

        items = paragraph["items"]

        if items:
            grouped_items = Chunker._create_grouped_items(
                option=option,
                items=items
            )
            paragraph_number = paragraph["paragraph_number"]
            paragraph_content = paragraph["paragraph_content"]
            ending = paragraph["ending"]

            for group in grouped_items:
                text_pieces = []
                items_included = []
                for item in group:
                    item_content = item["item_content"]
                    item_letter = item["item_letter"]

                    sub_items = item["sub_items"]
                    if sub_items:
                        for idx, sub_item_content in enumerate(sub_items):
                            text_pieces.append(f"{item_content} {sub_item_content}")
                            items_included.append({
                                "item_letter": item_letter,
                                "sub_item_number": idx+1,
                            })
                    else:
                        text_pieces.append(f"{item_content}")
                        items_included.append({
                            "item_letter": item_letter,
                            "sub_item_number": None,
                        })

                text = "\n".join(text_pieces)
                if include_paragraph_content:
                    text = f"{paragraph_content} {text}"
                if ending:
                    text = f"{text} {ending}"

                payload = {
                    "text": text,
                    "paragraph_number": paragraph_number,
                    "items_included": items_included,
                }
                payloads.append(payload)

            if not include_paragraph_content:
                payloads.append({
                    "text": paragraph["paragraph_content"],
                    "paragraph_number": paragraph["paragraph_number"],
                    "items_included": [],
                })
        else:
            payloads.append({
                "text": paragraph["paragraph_content"],
                "paragraph_number": paragraph["paragraph_number"],
                "items_included": [],
            })

        return payloads

    @staticmethod
    def run(tree: dict, config: ChunkerConfig) -> list[dict]:

        main_title = tree["main_title"]
        chunks = []

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

                        payloads = Chunker._create_payloads_by_paragraph(option=option,
                                                                         paragraph=paragraph)

                        for payload in payloads:
                            payload["main_title"] = main_title
                            payload["chapter_name"] = chapter["chapter_name"]
                            payload["chapter_number"] = chapter["chapter_number"]
                            payload["article_title"] = title["title_name"]
                            payload["article_number"] = article["article_number"]

                            payload["id"] = Chunker._create_id(payload)

                            embedding_text = Chunker._create_embedding_text(payload)
                            save_id = str(uuid.uuid4())

                            chunks.append({
                                "id": save_id,
                                "embedding_text": embedding_text,
                                "payload": payload,
                            })

        return chunks