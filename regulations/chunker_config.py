from typing import Literal, TypedDict


class ChunkerOption(TypedDict):
    item_merge: Literal["full", "none", "partial"]
    item_group_sizes: tuple[int, ...] | None

class ChunkerConfig:

    def __init__(self):
        self.options: dict[tuple[int, int, int], ChunkerOption] = {}

    def add_option(
        self,
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
        item_merge: Literal["full", "none", "partial"],
        item_group_sizes: tuple[int, ...] | None = None,
    ) -> None:

        key = (chapter_number, article_number, paragraph_number)

        self.options[key] = {
            "item_merge": item_merge,
            "item_group_sizes": item_group_sizes,
        }

    def get_option(
        self,
        chapter_number: int,
        article_number: int,
        paragraph_number: int,
    ) -> ChunkerOption:

        return self.options.get(
            (chapter_number, article_number, paragraph_number),
            {"item_merge": "full", "item_group_sizes": None},
        )