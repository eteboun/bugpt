from typing import Literal, ClassVar
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass(frozen=True)
class ParagraphLocation:
    chapter_number: int
    article_number: int
    paragraph_number: int

@dataclass(frozen=True)
class TableLocation:
    paragraph_location: ParagraphLocation
    table_number: int

@dataclass
class ItemPiece:
    start: int
    end: int
    include_paragraph_text: bool

@dataclass
class SubItemBinding:
    sub_item_merge: bool

@dataclass
class ItemOption:
    include_paragraph_text: bool
    item_merge: Literal["full", "none", "partial"]

    item_pieces: list[ItemPiece]
    sub_item_bindings: dict[int, SubItemBinding]

@dataclass
class TableOption:
    row_text_format: str

@dataclass
class Options:
    item_options: dict[ParagraphLocation, ItemOption] = field(default_factory=dict)
    table_options: dict[TableLocation, TableOption] = field(default_factory=dict)

class ChunkerConfig:

    DEFAULT_TABLE_OPTION: ClassVar[TableOption] = TableOption(
                                                    row_text_format=""
                                                )

    DEFAULT_ITEM_OPTION: ClassVar[ItemOption] = ItemOption(
                                include_paragraph_text=True,
                                item_merge="none",
                                item_pieces=[],
                                sub_item_bindings={},
                            )

    DEFAULT_SUB_ITEM_BINDING: ClassVar[SubItemBinding] = SubItemBinding(
        sub_item_merge=True,
    )


    def __init__(self, config_name: str) -> None:
        self.options = Options()
        self._load_options(config_name=config_name)

    def _load_options(self, config_name: str) -> None:

        path = Path(__file__).resolve().parent.parent / "configs" / f"{config_name}.json"
        config = json.loads(path.read_text(encoding="utf-8"))\
            if path.exists()\
            else {}

        for option in config.get("item", []):

            for full_item in option["full"]:

                paragraph_location = ParagraphLocation(
                    chapter_number=full_item["chapter_number"],
                    article_number=full_item["article_number"],
                    paragraph_number=full_item["paragraph_number"],
                )

            include_paragraph_text = option.get("include_paragraph_text",
                                                self.DEFAULT_ITEM_OPTION.include_paragraph_text)

            item_pieces = []
            for item_piece in option.get("item_pieces", []):
                interval = item_piece["interval"]
                include_paragraph_text = item_piece.get("include_paragraph_text", include_paragraph_text)

                item_pieces.append(ItemPiece(
                    start=interval[0],
                    end=interval[1],
                    include_paragraph_text=include_paragraph_text
                ))

            sub_item_bindings = {}
            for sub_item_piece in option.get("sub_item_bindings", []):
                item_number = sub_item_piece["item_number"]
                sub_item_merge = sub_item_piece.get("sub_item_merge",
                                                    self.DEFAULT_SUB_ITEM_BINDING.sub_item_merge)

                sub_item_bindings[item_number] = SubItemBinding(
                    sub_item_merge=sub_item_merge
                )

            self.options.item_options[paragraph_location] = ItemOption(
                include_paragraph_text=include_paragraph_text,
                item_merge=option.get("item_merge",
                                      self.DEFAULT_ITEM_OPTION.item_merge),

                item_pieces=item_pieces,
                sub_item_bindings=sub_item_bindings
            )

        for option in config.get("table", []):

            paragraph_location = ParagraphLocation(
                chapter_number=option["chapter_number"],
                article_number=option["article_number"],
                paragraph_number=option["paragraph_number"],
            )

            table_location = TableLocation(
                paragraph_location=paragraph_location,
                table_number=option["table_number"],
            )

            self.options.table_options[table_location] = TableOption(
                row_text_format=option.get("row_text_format",
                                           self.DEFAULT_TABLE_OPTION.row_text_format),
            )

    def get_item_option(self,
                        chapter_number: int,
                        article_number: int,
                        paragraph_number: int,
    ) -> ItemOption:

        paragraph_location = ParagraphLocation(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph_number,
        )

        return self.options.item_options.get(paragraph_location, self.DEFAULT_ITEM_OPTION)

    def get_table_option(self,
                         chapter_number: int,
                         article_number: int,
                         paragraph_number: int,
                         table_number: int,
    ) -> TableOption:

        paragraph_location = ParagraphLocation(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph_number,
        )

        table_location = TableLocation(
            paragraph_location=paragraph_location,
            table_number=table_number,
        )

        return self.options.table_options.get(table_location, self.DEFAULT_TABLE_OPTION)

    def get_sub_item_binding(
            self,
            option: ItemOption,
            item_number: int
    ) -> SubItemBinding:

        return option.sub_item_bindings.get(item_number, self.DEFAULT_SUB_ITEM_BINDING)
