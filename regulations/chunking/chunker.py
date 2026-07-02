import uuid
import re

from typing import ClassVar
from regulations.chunking.chunker_config import ChunkerConfig, ListedOption, TabularOption
from regulations.chunking.chunk_structure import *
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

        if payload.kind == "item_group":
            item_ids = []
            for item_included in payload.content:

                item_id = f"{item_included.general_item_number}.{item_included.sub_item_number}"\
                    if item_included.sub_item_number \
                    else str(item_included.general_item_number)

                item_ids.append(item_id)

            final_item_id = f"items_{"_".join(item_ids)}"
            id_items.append(final_item_id)

        elif payload.kind == "table":

            table_id = f"table_{payload.content.table_number:02d}"
            id_items.append(table_id)

        id_ = ":".join(id_items)

        return id_

    @staticmethod
    def _create_embedding_text(payload: Payload) -> str:

        parts = [
            f'Belge: {payload.main_title}',
            f'Bölüm: {payload.chapter_number}',
            f'Madde {payload.article_number}: {payload.article_title}',
        ]

        if payload.kind == "item_group":
            parts.append(f'Paragraf {payload.paragraph_number}')
            item_displays = []

            for item_included in payload.content:

                item_display = f"{item_included.general_item_number}.{item_included.sub_item_number}"\
                    if item_included.sub_item_number \
                    else str(item_included.general_item_number)

                item_displays.append(item_display)

            display_text = f"Bentler {", ".join(item_displays)}: {payload.text}"
            parts.append(display_text)

        elif payload.kind == "table":
            parts.append(f'Paragraf {payload.paragraph_number}')

            table = payload.content
            display_text = f"Tablo {table.table_number}: {payload.text}"
            parts.append(display_text)

        else:
            parts.append(f'Paragraf {payload.paragraph_number}: {payload.text}')

        embedding_text = "\n".join(parts)
        return f"passage: {embedding_text}"

    @staticmethod
    def _create_chunked_items(
            option: ListedOption,
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

    def _create_chunk(self, payload: Payload) -> Chunk:

        embedding_text = self._create_embedding_text(payload)

        return Chunk(
            embedding_text=embedding_text,
            id=str(uuid.uuid4()),
            payload=payload,
        )

    @staticmethod
    def _create_table_text(
            option: TabularOption,
            table: Table) -> str:

        row_texts = []
        formattable = option.row_text_format
        for row in table.rows:

            row_text = formattable.format(*row.content)
            row_texts.append(row_text)

        return "\n".join(row_texts)

    def _create_payloads(self,
                         main_title: str,
                         chapter_name: str,
                         article_title:str,
                          chapter_number: int,
                          article_number: int,
                         article_kind: Literal["temporary", "default"],
                          paragraph: Paragraph) -> list[Payload]:

        paragraph_number = paragraph.number

        payloads = []
        item_blocks = paragraph.item_blocks

        if item_blocks:

            table_count = 0
            for item_block in item_blocks:

                option = self.config.get_option(
                    kind=item_block.kind,
                    chapter_number=chapter_number,
                    article_number=article_number,
                    paragraph_number=paragraph_number,
                    item_block_number=item_block.local_index + 1
                )

                if item_block.kind == "listed":

                    items = item_block.content
                    chunked_items = Chunker._create_chunked_items(
                        option=option,
                        items=items
                    )

                    for group in chunked_items:
                        text_pieces = []
                        items_included = []
                        single_items_with_sub_items = []

                        for item in group:
                            if item.sub_items:
                                if len(group) != 1:
                                    for sub_item in item.sub_items:
                                        text_pieces.append(f"{item.text} {sub_item.text}")

                                        items_included.append(
                                            ItemIncluded(label=item.label,
                                                         sub_item_number=sub_item.local_index+1,
                                                         local_item_number=item.local_index+1,
                                                         general_item_number=item.general_index+1,
                                                         item_block_number=item_block.local_index+1)
                                        )
                                else:
                                    single_items_with_sub_items.append(item)
                            else:
                                text_pieces.append(f"{item.text}")

                                items_included.append(
                                    ItemIncluded(label=item.label,
                                                 sub_item_number=None,
                                                 local_item_number=item.local_index+1,
                                                 general_item_number=item.general_index+1,
                                                 item_block_number=item_block.local_index+1)
                                )

                        text = "\n".join(text_pieces)
                        if option.include_paragraph_content:
                            text = f"{paragraph.text} {text}"
                        if item_block.ending:
                            text = f"{text} {item_block.ending}"

                        payloads.append(ListedPayload(
                            paragraph_number=paragraph.number,
                            content=items_included,
                            text=text,
                        ))

                        if single_items_with_sub_items:
                            for item in single_items_with_sub_items:
                                for sub_item in item.sub_items:
                                    text = f"{paragraph.text} {item.text} {sub_item.text}"
                                    items_included = [
                                        ItemIncluded(label=item.label,
                                                     sub_item_number=sub_item.local_index+1,
                                                     local_item_number=item.local_index+1,
                                                     general_item_number=item.general_index+1,
                                                     item_block_number=item_block.local_index+1)
                                    ]

                                    payloads.append(ListedPayload(
                                        paragraph_number=paragraph.number,
                                        content=items_included,
                                        text=text,
                                    ))

                    if not option.include_paragraph_content:
                        payloads.append(EmptyPayload(
                            paragraph_number=paragraph.number,
                            text=paragraph.text,
                        ))
                else:
                    table_text = self._create_table_text(table=item_block.content,
                                                         option=option)
                    text = f"{paragraph.text}\n{table_text}"

                    payloads.append(TabularPayload(
                        paragraph_number=paragraph.number,
                        content=TableIncluded(
                            item_block_number=item_block.local_index+1,
                            table_number=table_count+1
                        ),
                        text=text,
                    ))

                    table_count += 1
        else:
            payloads.append(EmptyPayload(
                paragraph_number=paragraph.number,
                text=paragraph.text,
            ))

        for payload in payloads:
            payload.main_title = main_title
            payload.article_title = article_title
            payload.chapter_number = chapter_number
            payload.chapter_name = chapter_name
            payload.article_number = article_number
            payload.article_kind = article_kind
            payload.id = self._create_id(payload)

        return payloads

    def run(self, document: Document) -> list[Chunk]:

        document_title = document.title
        chunks = []

        for chapter in document.chapters:
            for title in chapter.titles:
                for article in title.articles:
                    for paragraph in article.paragraphs:

                        payloads = self._create_payloads(
                            main_title=document_title,
                            chapter_name=chapter.name,
                            chapter_number=chapter.number,
                            article_title=title.name,
                            article_number=article.number,
                            article_kind=article.kind,
                            paragraph=paragraph
                        )

                        for payload in payloads:
                            chunks.append(
                                self._create_chunk(payload=payload)
                            )

        return chunks