from typing import Literal, ClassVar
from dataclasses import dataclass, field
from pathlib import Path
import json

@dataclass(frozen=True)
class Location:
    chapter_number: int
    article_number: int
    paragraph_number: int
    item_block_number: int

@dataclass
class ListedOption:
    include_paragraph_content: bool
    item_merge: Literal["full", "none", "partial"]
    item_group_sizes: tuple[int, ...] | None

@dataclass
class TabularOption:
    row_text_format: str

@dataclass
class Options:
    listed_options: dict[Location, ListedOption] = field(default_factory=dict)
    tabular_options: dict[Location, TabularOption] = field(default_factory=dict)

class ChunkerConfig:

    DEFAULT_TABULAR_OPTION: ClassVar[TabularOption] = TabularOption(
                                                    row_text_format=""
                                                )

    DEFAULT_LISTED_OPTION: ClassVar[ListedOption] = ListedOption(
                                include_paragraph_content=True,
                                item_merge="none",
                                item_group_sizes=None
                            )


    def __init__(self, config_name: str) -> None:
        self.options = Options()
        self._load_options(config_name=config_name)

    def _load_options(self, config_name: str) -> None:

        path = Path(__file__).resolve().parent.parent / "configs" / f"{config_name}.json"
        config = json.loads(path.read_text(encoding="utf-8"))\
            if path.exists()\
            else {}

        for option in config.get("listed", []):
            location = Location(
                chapter_number=option["chapter_number"],
                article_number=option["article_number"],
                paragraph_number=option["paragraph_number"],
                item_block_number=option.get("item_block_number", 1),
            )

            self.options.listed_options[location] = ListedOption(
                include_paragraph_content=option.get("include_paragraph_content", True),
                item_merge=option.get("item_merge", "none"),
                item_group_sizes=option.get("item_group_sizes", None),
            )

        for option in config.get("tabular", []):

            location = Location(
                chapter_number=option["chapter_number"],
                article_number=option["article_number"],
                paragraph_number=option["paragraph_number"],
                item_block_number=option.get("item_block_number", 1),
            )

            self.options.tabular_options[location] = TabularOption(
                row_text_format=option.get("row_text_format", ""),
            )

    def get_option(
        self,
        kind: Literal["tabular", "listed"],
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
        item_block_number: int = 1
    ) -> ListedOption | TabularOption:

        location = Location(
            chapter_number=chapter_number,
            article_number=article_number,
            paragraph_number=paragraph_number,
            item_block_number=item_block_number,
        )

        if kind == "tabular":
            return self.options.tabular_options.get(location, self.DEFAULT_TABULAR_OPTION)

        elif kind == "listed":
            return self.options.listed_options.get(location, self.DEFAULT_LISTED_OPTION)

        else:
            raise Exception(f"Unknown option kind: {kind}")
