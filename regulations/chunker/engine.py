import uuid
import re

from typing import ClassVar
from regulations.chunker.config import ChunkerConfig, TableOption
from regulations.chunker.models import *
from regulations.models import *

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

        base_slug = (payload.document_name
                     .translate(Chunker.TR_MAP)
                     .lower()
                     .replace(" ", "_"))
        base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

        chapter_id = f"chapter_{payload.chapter_number:02d}"
        article_id = f"article_{payload.article_number:02d}"
        paragraph_id = f"paragraph_{payload.paragraph_number:02d}"

        id_items = [base_slug, chapter_id, article_id, paragraph_id]

        if payload.kind == "item":
            item_ids = []
            sub_item_ids = []
            for item_included in payload.content:

                for sub_item in item_included.included_sub_items:
                    sub_item_ids.append(
                        f"{item_included.item_number:02d}.{sub_item.sub_item_number:02d}"
                    )

                item_id = f"{item_included.item_number:02d}"
                item_ids.append(item_id)

            final_item_id = f"items_{"_".join(item_ids)}"
            id_items.append(final_item_id)

            if sub_item_ids:
                final_sub_item_id = f"sub_items_{"_".join(sub_item_ids)}"
                id_items.append(final_sub_item_id)

        elif payload.kind == "table":

            table_id = f"table_{payload.content.table_number:02d}"
            id_items.append(table_id)

        id_ = ":".join(id_items)

        return id_

    @staticmethod
    def _create_embedding_text(payload: Payload) -> str:

        parts = [
            f'Belge: {payload.document_name}',
            f'Bölüm: {payload.chapter_name}',
            f'Başlık: {payload.article_title}',
            f'İçerik: {payload.text}'
        ]

        embedding_text = "\n".join(parts)
        return embedding_text

    @staticmethod
    def _flatten_unsplittable_item_to_flattened_item(item: Item) -> FlattenedItem:

        if item.sub_items:

            included_sub_items = []
            sub_item_texts = []
            for sub_item in item.sub_items:
                included_sub_items.append(FlattenedSubItem(
                    text=sub_item.text,
                    label=sub_item.label,
                    sub_item_number=sub_item.local_index + 1
                ))
                sub_item_texts.append(sub_item.text)

            flattened_item_text = (f"{item.text}\n"
                                   f"{"\n".join(sub_item_texts)}"
                                   f"{"\n" + item.ending if item.ending else ''}")

            return FlattenedItem(
                text=flattened_item_text,
                label=item.label,
                item_number=item.general_index + 1,
                included_sub_items=included_sub_items
            )

        else:

            flattened_item_text = (f"{item.text}"
                                   f"{" " + item.ending if item.ending else ''}")

            return FlattenedItem(
                text=flattened_item_text,
                label=item.label,
                item_number=item.general_index + 1,
                included_sub_items=[]
            )

    @staticmethod
    def _flatten_unsplittable_item_group_to_flattened_item_group(group: ItemGroup) -> FlattenedItemGroup:

        flattened_items: list[FlattenedItem] = []
        for item in group.items:
            flattened_items.append(
                Chunker._flatten_unsplittable_item_to_flattened_item(item=item)
            )

        return FlattenedItemGroup(
            items=flattened_items,
            include_paragraph_text=group.include_paragraph_text
        )

    @staticmethod
    def _flatten_splittable_item_group_to_item_groups(group: ItemGroup) -> list[FlattenedItemGroup]:

        item = group.items[0]
        flattened_item_groups: list[FlattenedItemGroup] = []
        for sub_item in item.sub_items:
            included_sub_items = [FlattenedSubItem(
                text=sub_item.text,
                label=sub_item.label,
                sub_item_number=sub_item.local_index + 1
            )]
            flattened_item_text = (f"{item.text}\n"
                                   f"{sub_item.text}"
                                   f"{"\n" + item.ending if item.ending else ''}")

            flattened_item_groups.append(FlattenedItemGroup(
                items=[FlattenedItem(
                    text=flattened_item_text,
                    label=item.label,
                    item_number=item.general_index + 1,
                    included_sub_items=included_sub_items
                )],
                include_paragraph_text=group.include_paragraph_text
            ))

        return flattened_item_groups

    def _flatten_item_groups(self,
                             chapter_number: int,
                             article_number: int,
                             paragraph_number: int,
                             item_groups: list[ItemGroup]
                             ) -> list[FlattenedItemGroup]:

        flattened_item_groups: list[FlattenedItemGroup] = []

        for group in item_groups:

            is_singleton = len(group.items) == 1
            has_sub_items = bool(group.items[0].sub_items)
            merge = self.config.get_sub_item_option(
                chapter_number=chapter_number,
                article_number=article_number,
                paragraph_number=paragraph_number,
                item_number=group.items[0].general_index+1
            ).merge

            if is_singleton and has_sub_items and not merge:

                flattened_item_groups.extend(
                    self._flatten_splittable_item_group_to_item_groups(group=group)
                )

            else:

                flattened_item_groups.append(
                    self._flatten_unsplittable_item_group_to_flattened_item_group(group=group)
                )

        return flattened_item_groups

    def _create_item_groups(self,
                            chapter_number: int,
                            article_number: int,
                            paragraph: Paragraph,
                            ) -> list[ItemGroup]:

        item_groups: list[ItemGroup] = []
        if items := paragraph.content.items:

            item_option = self.config.get_item_option(
                chapter_number=chapter_number,
                article_number=article_number,
                paragraph_number=paragraph.number
            )

            if item_option.merge == "full":
                group = ItemGroup(
                    items=items,
                    include_paragraph_text=item_option.include_paragraph_text,
                )
                item_groups.append(group)

            elif item_option.merge == "none":
                for item in items:
                    group = ItemGroup(
                        items=[item],
                        include_paragraph_text=item_option.include_paragraph_text,
                    )
                    item_groups.append(group)

            else:
                for part in item_option.parts:

                    start = part.start
                    end = part.end
                    include_paragraph_text = part.include_paragraph_text

                    group = ItemGroup(
                        items=items[start:end],
                        include_paragraph_text=include_paragraph_text,
                    )

                    item_groups.append(group)

        return item_groups

    def _create_chunked_item_group(
            self,
            chapter_number: int,
            article_number: int,
            paragraph: Paragraph
    ) -> ChunkedItemGroup:

        item_groups = self._create_item_groups(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph=paragraph
        )

        flattened_item_groups = self._flatten_item_groups(
            item_groups=item_groups,
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph.number
        )

        chunked_items: list[ChunkedItem] = []
        consumed_paragraph_text: bool = False
        for flattened_items in flattened_item_groups:

            chunked_piece_text = (f"{paragraph.text + "\n" if flattened_items.include_paragraph_text else ''}\n"
                                  f"{"\n\n".join([item.text for item in flattened_items.items])}")

            chunked_items.append(ChunkedItem(
                text=chunked_piece_text,
                flattened_items=flattened_items.items
            ))

            consumed_paragraph_text |= flattened_items.include_paragraph_text

        return ChunkedItemGroup(
            items=chunked_items,
            consumed_paragraph_text=consumed_paragraph_text
        )

    @staticmethod
    def _create_chunk(payload: Payload) -> Chunk:

        return Chunk(
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
                         document_type: str,
                         document_name: str,
                         chapter_name: str,
                         article_title:str,
                         chapter_number: int,
                         article_number: int,
                         article_kind: Literal["temporary", "default"],
                         paragraph: Paragraph
                         ) -> list[Payload]:

        payloads = []
        consumed_paragraph_text: bool = False

        chunked_item_group = self._create_chunked_item_group(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph=paragraph
        )
        consumed_paragraph_text |= chunked_item_group.consumed_paragraph_text

        for chunked_item in chunked_item_group.items:
            text = chunked_item.text
            items_included = [ItemIncluded(
                label=flattened_item.label,
                item_number=flattened_item.item_number,
                included_sub_items=[SubItemIncluded(
                    label=sub_item.label,
                    sub_item_number=sub_item.sub_item_number
                ) for sub_item in flattened_item.included_sub_items]
            ) for flattened_item in chunked_item.flattened_items]

            content = items_included or None
            kind: Literal["item", "paragraph"] = "item" if content else "paragraph"

            payloads.append(Payload(
                text=text,
                content=content,
                kind=kind
            ))

        for table in paragraph.content.tables:
            table_number = table.local_index+1

            table_option = self.config.get_table_option(
                chapter_number=chapter_number,
                article_number=article_number,
                paragraph_number=paragraph.number,
                table_number=table_number
            )
            consumed_paragraph_text |= table_option.include_paragraph_text

            table_text = self._create_table_text(
                table=table,
                option=table_option,
            )

            text = f"{paragraph.text}\n{table_text}"\
                if table_option.include_paragraph_text\
                else table_text

            table_included = TableIncluded(
                    table_number=table_number
                )

            payloads.append(Payload(
                kind="table",
                content=table_included,
                text=text,
            ))

        if not consumed_paragraph_text:
            payloads.append(Payload(
                kind="paragraph",
                text=paragraph.text,
                content=None,
            ))

        for payload in payloads:
            payload.document_type = document_type
            payload.document_name = document_name
            payload.article_title = article_title
            payload.chapter_number = chapter_number
            payload.chapter_name = chapter_name
            payload.article_number = article_number
            payload.article_kind = article_kind
            payload.paragraph_number = paragraph.number

            payload.id = self._create_id(payload)
            payload.embedding_text = self._create_embedding_text(payload)

        return payloads

    def run(self, document: Document) -> list[Chunk]:

        document_name = document.name
        chunks = []

        for chapter in document.chapters:
            for title in chapter.titles:
                for article in title.articles:
                    for paragraph in article.paragraphs:

                        payloads = self._create_payloads(
                            document_type=document.document_type,
                            document_name=document_name,
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