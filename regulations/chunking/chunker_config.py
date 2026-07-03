from typing import Literal, ClassVar
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass(frozen=True)
class Location:
    chapter_number: int
    article_number: int
    paragraph_number: int

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
    item_options: dict[Location, ItemOption] = field(default_factory=dict)
    table_options: dict[Location, TableOption] = field(default_factory=dict)

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
        sub_item_merge=False,
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
            location = Location(
                chapter_number=option["chapter_number"],
                article_number=option["article_number"],
                paragraph_number=option["paragraph_number"],
            )

            item_pieces = []
            for item_piece in option["item_pieces"]:
                interval = item_piece["interval"]
                include_paragraph_text = item_piece["include_paragraph_text"]

                item_pieces.append(ItemPiece(
                    start=interval[0],
                    end=interval[1],
                    include_paragraph_text=include_paragraph_text
                ))

            sub_item_bindings = {}
            for sub_item_piece in option["sub_item_bindings"]:
                item_number = sub_item_piece["item_number"]
                sub_item_merge = sub_item_piece["sub_item_merge"]

                sub_item_bindings[item_number] = SubItemBinding(
                    sub_item_merge=sub_item_merge
                )

            self.options.item_options[location] = ItemOption(
                include_paragraph_text=option.get("include_paragraph_text", True),
                item_merge=option.get("item_merge", "none"),

                item_pieces=item_pieces,
                sub_item_bindings=sub_item_bindings
            )

        for option in config.get("table", []):

            location = Location(
                chapter_number=option["chapter_number"],
                article_number=option["article_number"],
                paragraph_number=option["paragraph_number"],
            )

            self.options.table_options[location] = TableOption(
                row_text_format=option.get("row_text_format", ""),
            )

    def get_option(
        self,
        kind: Literal["table", "item"],
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
    ) -> ItemOption | TableOption:

        location = Location(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph_number,
        )

        if kind == "table":
            return self.options.table_options.get(location, self.DEFAULT_TABLE_OPTION)

        elif kind == "item":
            return self.options.item_options.get(location, self.DEFAULT_ITEM_OPTION)

        else:
            raise Exception(f"Unknown option kind: {kind}")

    def get_sub_item_binding(
            self,
            option: ItemOption,
            item_number: int
    ) -> SubItemBinding:

        return option.sub_item_bindings.get(item_number, self.DEFAULT_SUB_ITEM_BINDING)
