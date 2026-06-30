import uuid
import re

from typing import ClassVar
from regulations.chunking.chunk_structure import ItemIncluded, Payload, Chunk
from regulations.chunking.chunker_config import ChunkerConfig, ChunkerOption
from regulations.document_structure import *


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
            for item_included in payload.items_included:

                item_id = f"{item_included.number}.{item_included.sub_item_number}"\
                    if item_included.sub_item_number \
                    else str(item_included.number)

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

        if payload.items_included:
            parts.append(f'Paragraf {payload.paragraph_number}')
            item_displays = []

            for item_included in payload.items_included:

                item_display = f"{item_included.number}.{item_included.sub_item_number}"\
                    if item_included.sub_item_number \
                    else str(item_included.number)

                item_displays.append(item_display)

            display_text = f"Bentler {", ".join(item_displays)}: {payload.text}"
            parts.append(display_text)
        else:
            parts.append(f'Paragraf {payload.paragraph_number}: {payload.text}')

        embedding_text = "\n".join(parts)
        return embedding_text

    @staticmethod
    def _create_chunked_items(
            option: ChunkerOption,
            items: list[Item],
    ) -> list[list[Item]]:

        if option.item_merge == "full":
            return [items]

        if option.item_merge == "none":
            return [[item] for item in items]

        if not option.item_group_sizes or sum(option.item_group_sizes) != len(items):
            raise ValueError("Invalid item_group_sizes")

        groups: list[list[Item]] = []
        last = 0

        for size in option.item_group_sizes:
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
                          paragraph: Paragraph) -> list[Chunk]:

        paragraph_number = paragraph.number

        payloads = []
        item_groups = paragraph.item_groups

        if item_groups:
            for item_group in item_groups:

                option = self.config.get_option(
                    chapter_number=chapter_number,
                    article_number=article_number,
                    paragraph_number=paragraph_number,
                    item_group_number=item_group.local_index+1
                )

                items = item_group.items
                chunked_items = Chunker._create_chunked_items(
                    option=option,
                    items=items
                )

                for group in chunked_items:
                    text_pieces = []
                    items_included = []
                    for item in group:

                        if item.sub_items:

                            for sub_item in item.sub_items:
                                text_pieces.append(f"{item.text} {sub_item.text}")

                                items_included.append(
                                    ItemIncluded(label=item.label,
                                                 sub_item_number=sub_item.local_index+1,
                                                 number=item.local_index+1)
                                )
                        else:
                            text_pieces.append(f"{item.text}")

                            items_included.append(
                                ItemIncluded(label=item.label,
                                             sub_item_number=None,
                                             number=item.local_index+1)
                            )

                    text = "\n".join(text_pieces)
                    if option.include_paragraph_content:
                        text = f"{paragraph.text} {text}"
                    if item_group.ending:
                        text = f"{text} {item_group.ending}"

                    payloads.append(Payload(
                        paragraph_number=paragraph.number,
                        items_included=items_included,
                        text=text,
                    ))

                if not option.include_paragraph_content:
                    payloads.append(Payload(
                        paragraph_number=paragraph.number,
                        items_included=[],
                        text=paragraph.text,
                    ))
        else:
            payloads.append(Payload(
                paragraph_number=paragraph.number,
                items_included=[],
                text=paragraph.text,
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

    def run(self, document: Document) -> list[Chunk]:

        document_title = document.title
        chunks = []

        for chapter in document.chapters:
            for title in chapter.titles:
                for article in title.articles:
                    for paragraph in article.paragraphs:

                        chunks.extend(self._create_chunks(
                            main_title=document_title,
                            chapter_name=chapter.name,
                            chapter_number=chapter.number,
                            article_title=title.name,
                            article_number=article.number,
                            paragraph=paragraph
                        ))

        return chunks