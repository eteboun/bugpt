from typing import Literal
from dataclasses import dataclass

@dataclass
class ChunkerOption:
    include_paragraph_content: bool
    item_merge: Literal["full", "none", "partial"]
    item_group_sizes: tuple[int, ...] | None

class ChunkerConfig:

    def __init__(self):
        self.options: dict[tuple[int, int, int, int], ChunkerOption] = {}

    def add_option(
        self,
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
        item_group_number: int = 1,
        include_paragraph_content: bool = True,
        item_merge: Literal["full", "none", "partial"] = "none",
        item_group_sizes: tuple[int, ...] | None = None,
    ) -> None:

        key = (chapter_number, article_number, paragraph_number, item_group_number)

        self.options[key] = ChunkerOption(
            include_paragraph_content=include_paragraph_content,
            item_merge=item_merge,
            item_group_sizes=item_group_sizes,
        )

    def add_options(
            self,
            option_list: list[dict[str, int | bool | tuple[int, ...] | Literal["full", "none", "partial"] | None]]
    ) -> None:

        for option in option_list:
            self.add_option(**option)

    def get_option(
        self,
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
        item_group_number: int = 1
    ) -> ChunkerOption:

        return self.options.get(
            (chapter_number, article_number, paragraph_number, item_group_number),
            {"item_merge": "none", "item_group_sizes": None, "include_paragraph_content": True},
        )