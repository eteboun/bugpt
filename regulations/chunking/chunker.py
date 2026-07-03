import uuid
import re

from typing import ClassVar
from regulations.chunking.chunker_config import ChunkerConfig, ItemOption, TableOption
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

    def _create_chunked_items(
            self,
            paragraph_text: str,
            option: ItemOption,
            items: list[Item],
    ) -> list[ChunkedPiece]:

        if not items:
            return [ChunkedPiece(
                text=paragraph_text,
                flattened_items=[]
            )]

        item_groups: list[ItemGroup] = []
        if option.item_merge == "full":
            group = ItemGroup(
                items=items,
                include_paragraph_text=option.include_paragraph_text,
            )
            item_groups.append(group)

        elif option.item_merge == "none":
            for item in items:
                group = ItemGroup(
                    items=[item],
                    include_paragraph_text=option.include_paragraph_text,
                )
                item_groups.append(group)

        else:
            for piece in option.item_pieces:
                start = piece.start
                end = piece.end
                include_paragraph_text = piece.include_paragraph_text

                group = ItemGroup(
                    items=items[start:end],
                    include_paragraph_text=include_paragraph_text,
                )
                item_groups.append(group)

        chunked_pieces = []
        consumed_paragraph_text = False
        for group in item_groups:
            flattened_items = []
            consumed_paragraph_text |= group.include_paragraph_text

            for item in group.items:
                if item.sub_items:
                    sub_item_merge = self.config.get_sub_item_binding(
                        option=option,
                        item_number=item.general_index+1
                    )

                    if sub_item_merge:

                        included_sub_items = []
                        sub_item_texts = []
                        for sub_item in item.sub_items:

                            included_sub_items.append(FlattenedSubItem(
                                text=sub_item.text,
                                label=sub_item.label,
                                sub_item_number=sub_item.local_index+1
                            ))
                            sub_item_texts.append(sub_item.text)

                        flattened_item_text = (f"{item.text}\n"
                                               f"{"\n".join(sub_item_texts)}"
                                               f"{"\n" + item.ending if item.ending else ''}")
                        flattened_items.append(FlattenedItem(
                            text=flattened_item_text,
                            label=item.label,
                            item_number=item.general_index+1,
                            included_sub_items=included_sub_items
                        ))

                    else:
                        for sub_item in item.sub_items:
                            included_sub_items = [FlattenedSubItem(
                                text=sub_item.text,
                                label=sub_item.label,
                                sub_item_number=sub_item.local_index+1
                            )]
                            flattened_item_text = (f"{item.text}\n"
                                                   f"{sub_item.text}"
                                                   f"{"\n" + item.ending if item.ending else ''}")
                            flattened_items.append(FlattenedItem(
                                text=flattened_item_text,
                                label=item.label,
                                item_number=item.general_index+1,
                                included_sub_items=included_sub_items
                            ))
                else:
                    flattened_item_text = (f"{item.text}"
                                           f"{" " + item.ending if item.ending else ''}")
                    flattened_items.append(FlattenedItem(
                        text=flattened_item_text,
                        label=item.label,
                        item_number=item.general_index+1,
                        included_sub_items=[]
                    ))

            chunked_piece_text = (f"{paragraph_text + "\n" if group.include_paragraph_text else ''}\n"
                                  f"{"\n\n".join([item.text for item in flattened_items])}")

            chunked_pieces.append(ChunkedPiece(
                text=chunked_piece_text,
                flattened_items=flattened_items
            ))

        if not consumed_paragraph_text:
            chunked_pieces.append(ChunkedPiece(
                text=paragraph_text,
                flattened_items=[]
            ))

        return chunked_pieces

    def _create_chunk(self, payload: Payload) -> Chunk:

        embedding_text = self._create_embedding_text(payload)

        return Chunk(
            embedding_text=embedding_text,
            id=str(uuid.uuid4()),
            payload=payload,
        )

    @staticmethod
    def _create_table_text(
            option: TableOption,
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

        payloads = []
        items = paragraph.content.items
        tables = paragraph.content.tables

        item_option = self.config.get_option(
            kind="item",
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph.number
        )

        chunked_items = self._create_chunked_items(
            paragraph_text=paragraph.text,
            option=item_option,
            items=items
        )

        for chunked_item in chunked_items:
            text = chunked_item.text
            items_included = [ItemIncluded(
                label=flattened_item.label,
                item_number=flattened_item.item_number,
                included_sub_items=[SubItemIncluded(
                    label=sub_item.label,
                    sub_item_number=sub_item.sub_item_number
                ) for sub_item in flattened_item.included_sub_items]
            ) for flattened_item in chunked_item.flattened_items]

            payloads.append(ItemPayload(
                text=text,
                content=items_included
            ))

        table_option = self.config.get_option(
            kind="table",
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph.number
        )

        for idx, table in enumerate(tables):
            table_text = self._create_table_text(
                table=table,
                option=table_option,
            )
            text = f"{paragraph.text}\n{table_text}"

            table_included = TableIncluded(
                    table_number=idx+1
                )

            payloads.append(TablePayload(
                content=table_included,
                text=text,
            ))

        for payload in payloads:
            payload.main_title = main_title
            payload.article_title = article_title
            payload.chapter_number = chapter_number
            payload.chapter_name = chapter_name
            payload.article_number = article_number
            payload.article_kind = article_kind
            payload.paragraph_number = paragraph.number
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