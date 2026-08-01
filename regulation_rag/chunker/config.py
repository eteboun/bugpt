from typing import Literal, ClassVar, TypeAlias
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

@dataclass(frozen=True)
class ItemLocation:
    paragraph_location: ParagraphLocation
    item_number: int

@dataclass
class ItemPart:
    start: int
    end: int
    include_paragraph_text: bool

@dataclass
class SubItemOption:
    merge: bool

@dataclass
class NonPartialItemOption:
    merge: Literal["full", "none"]
    include_paragraph_text: bool

@dataclass
class PartialItemOption:
    parts: list[ItemPart]
    merge: Literal["partial"] = "partial"

ItemOption: TypeAlias = NonPartialItemOption | PartialItemOption

@dataclass
class TableOption:
    row_text_format: str
    include_paragraph_text: bool

@dataclass
class Options:
    item_options: dict[ParagraphLocation, ItemOption] = field(default_factory=dict)
    sub_item_options: dict[ItemLocation, SubItemOption] = field(default_factory=dict)
    table_options: dict[TableLocation, TableOption] = field(default_factory=dict)

class ChunkerConfig:

    DEFAULT_TABLE_OPTION: ClassVar[TableOption] = TableOption(
                                                    row_text_format="",
                                                    include_paragraph_text=True
                                                )

    DEFAULT_ITEM_OPTION: ClassVar[NonPartialItemOption] = NonPartialItemOption(
                                include_paragraph_text=True,
                                merge="none",
                            )

    DEFAULT_SUB_ITEM_OPTION: ClassVar[SubItemOption] = SubItemOption(
        merge=True,
    )

    def __init__(self, config_name: str) -> None:
        self.options = Options()
        self._load_options(config_name=config_name)

    def _load_options(self, config_name: str) -> None:

        path = Path(__file__).resolve().parent.parent / "configs" / f"{config_name}.json"
        config = json.loads(path.read_text(encoding="utf-8"))\
            if path.exists()\
            else {}

        for option_type, item_configs in config.get("item", {}).items():
            for item_config in item_configs:
                paragraph_location = ParagraphLocation(
                    chapter_number=item_config["chapter_number"],
                    article_number=item_config["article_number"],
                    paragraph_number=item_config["paragraph_number"],
                )

                if option_type == "full" or option_type == "none":

                    include_paragraph_text = item_config.get("include_paragraph_text",
                                                        self.DEFAULT_ITEM_OPTION.include_paragraph_text)

                    self.options.item_options[paragraph_location] = NonPartialItemOption(
                        merge=option_type,
                        include_paragraph_text=include_paragraph_text,
                    )

                else:

                    item_parts = []
                    for part in item_config["parts"]:
                        interval = part["interval"]
                        start = interval[0]
                        end = interval[1]

                        include_paragraph_text = part.get("include_paragraph_text",
                                                        self.DEFAULT_ITEM_OPTION.include_paragraph_text)

                        item_part = ItemPart(
                            start=start,
                            end=end,
                            include_paragraph_text=include_paragraph_text
                        )
                        item_parts.append(item_part)

                    self.options.item_options[paragraph_location] = PartialItemOption(
                        parts=item_parts
                    )

        for sub_item_config in config.get("sub_item", []):

            paragraph_location = ParagraphLocation(
                chapter_number=sub_item_config["chapter_number"],
                article_number=sub_item_config["article_number"],
                paragraph_number=sub_item_config["paragraph_number"],
            )

            item_location = ItemLocation(
                paragraph_location=paragraph_location,
                item_number=sub_item_config["item_number"]
            )

            merge = sub_item_config.get("merge",
                                        self.DEFAULT_SUB_ITEM_OPTION.merge)

            self.options.sub_item_options[item_location] = SubItemOption(
                merge=merge
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

            include_paragraph_text = option.get("include_paragraph_text",
                                                self.DEFAULT_TABLE_OPTION.include_paragraph_text)
            row_text_format = option.get("row_text_format",
                                         self.DEFAULT_TABLE_OPTION.row_text_format)

            self.options.table_options[table_location] = TableOption(
                row_text_format=row_text_format,
                include_paragraph_text=include_paragraph_text
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

    def get_sub_item_option(
            self,
            chapter_number: int,
            article_number: int,
            paragraph_number: int,
            item_number: int
    ) -> SubItemOption:

        paragraph_location = ParagraphLocation(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph_number,
        )

        item_location = ItemLocation(
            paragraph_location=paragraph_location,
            item_number=item_number,
        )

        return self.options.sub_item_options.get(item_location, self.DEFAULT_SUB_ITEM_OPTION)
