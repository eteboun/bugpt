import uuid
from typing import ClassVar
from regulations.chunking.chunk_structure import ItemIncluded, Payload, Chunk
from regulations.chunking.chunker_config import ChunkerConfig, ChunkerOption
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

    def __init__(self, config: ChunkerConfig):
        self.config = config

    @staticmethod
    def _create_id(payload: Payload) -> str:

        base_slug = (payload.main_title
                     .translate(Chunker.TR_MAP)
                     .lower()
                     .replace(" ", "_"))
        base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

        chapter_id = f"chapter_{payload.chapter_number:02d}"
        article_id = f"article_{payload.article_number:02d}"
        paragraph_id = f"paragraph_{payload.paragraph_number:02d}"

        id_items = [base_slug, chapter_id, article_id, paragraph_id]

        if payload.items_included:
            item_ids = []
            for item in payload.items_included:

                item_id = f"{item.item_letter}_{item.sub_item_number}"\
                    if item.sub_item_number\
                    else item.item_letter
                item_ids.append(item_id)

            final_item_id = f"items_{"_".join(item_ids)}"
            id_items.append(final_item_id)

        id_ = ":".join(id_items)

        return id_

    @staticmethod
    def _create_embedding_text(payload: Payload) -> str:

        parts = [
            f'Belge: {payload.main_title}',
            f'Bölüm: {payload.chapter_number}',
            f'Madde {payload.article_number}: {payload.article_title}',
        ]

        text = payload.text

        items_included = payload.items_included
        if items_included:
            parts.append(f'Paragraf {payload.paragraph_number}')
            item_displays = []

            for item in items_included:
                item_letter = item.item_letter
                sub_item_number = item.sub_item_number

                item_display = f"{item_letter}.{sub_item_number}" if sub_item_number else item_letter
                item_displays.append(item_display)

            display_text = f"Bentler {", ".join(item_displays)}: {text}"
            parts.append(display_text)
        else:
            parts.append(f'Paragraf {payload.paragraph_number}: {text}')

        embedding_text = "\n".join(parts)

        return embedding_text

    @staticmethod
    def _create_chunked_items(
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

    def _create_chunks(self,
                         main_title: str,
                         chapter_name: str,
                         article_title:str,
                          chapter_number: int,
                          article_number: int,
                          paragraph: dict) -> list[Chunk]:

        paragraph_number = paragraph["paragraph_number"]

        payloads = []
        item_groups = paragraph["item_groups"]

        if item_groups:
            for idx, item_group in enumerate(item_groups):

                option = self.config.get_option(
                    chapter_number=chapter_number,
                    article_number=article_number,
                    paragraph_number=paragraph_number,
                    item_group_number=idx+1
                )
                include_paragraph_content = option["include_paragraph_content"]

                items = item_group["items"]
                chunked_items = Chunker._create_chunked_items(
                    option=option,
                    items=items
                )

                paragraph_number = paragraph["paragraph_number"]
                paragraph_content = paragraph["paragraph_content"]
                ending = item_group["ending"]

                for group in chunked_items:
                    text_pieces = []
                    items_included = []
                    for item in group:
                        item_content = item["item_content"]
                        item_letter = item["item_letter"]

                        sub_items = item["sub_items"]
                        if sub_items:
                            if len(group) != 1:
                                raise ValueError("invalid item chunk")

                            for idx_, sub_item_content in enumerate(sub_items):
                                text_pieces.append(f"{item_content} {sub_item_content}")

                                items_included.append(
                                    ItemIncluded(item_letter=item_letter,sub_item_number=idx_+1)
                                )
                        else:
                            text_pieces.append(f"{item_content}")

                            items_included.append(
                                ItemIncluded(item_letter=item_letter, sub_item_number=None)
                            )

                    text = "\n".join(text_pieces)
                    if include_paragraph_content:
                        text = f"{paragraph_content} {text}"
                    if ending:
                        text = f"{text} {ending}"

                    payloads.append(Payload(
                        paragraph_number=paragraph_number,
                        items_included=items_included,
                        text=text,
                    ))

                if not include_paragraph_content:
                    payloads.append(Payload(
                        paragraph_number=paragraph_number,
                        items_included=[],
                        text=paragraph["paragraph_content"],
                    ))
        else:
            payloads.append(Payload(
                paragraph_number=paragraph_number,
                items_included=[],
                text=paragraph["paragraph_content"],
            ))

        chunks = []
        for payload in payloads:
            payload.main_title = main_title
            payload.article_title = article_title
            payload.chapter_number = chapter_number
            payload.chapter_name = chapter_name
            payload.article_number = article_number

            payload.id = self._create_id(payload)

            embedding_text = self._create_embedding_text(payload)
            id_ = str(uuid.uuid4())

            chunks.append(
                Chunk(
                    payload=payload,
                    embedding_text=embedding_text,
                    id=id_
                )
            )

        return chunks

    def run(self, tree: dict) -> list[Chunk]:

        main_title = tree["main_title"]
        chunks = []

        for chapter in tree["chapters"]:
            for title in chapter["titles"]:
                for article in title["articles"]:
                    for paragraph in article["paragraphs"]:

                        chunks.extend(self._create_chunks(
                            main_title=main_title,
                            chapter_name=chapter["chapter_name"],
                            chapter_number=chapter["chapter_number"],
                            article_title=title["title_name"],
                            article_number=article["article_number"],
                            paragraph=paragraph
                        ))

        return chunks