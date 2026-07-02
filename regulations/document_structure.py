from dataclasses import dataclass, asdict, field
from typing import Literal, TypeAlias

@dataclass
class SubItem:
    text: str
    local_index: int

@dataclass
class Item:
    text: str
    label: str | None
    local_index: int
    general_index: int

    sub_items: list[SubItem]

@dataclass
class Row:
    content: list[str]
    local_index: int

@dataclass
class Table:
    row_titles: list[str]
    rows: list[Row]

@dataclass
class BaseItemBlock:
    local_index: int

@dataclass
class ListedItemBlock(BaseItemBlock):
    content: list[Item]
    ending: str | None
    kind: Literal["listed"] = field(default="listed", init=False)

@dataclass
class TabularItemBlock(BaseItemBlock):
    content: Table
    kind: Literal["tabular"] = field(default="tabular", init=False)

ItemBlock: TypeAlias = ListedItemBlock | TabularItemBlock

@dataclass
class Paragraph:
    number: int
    text: str

    item_blocks: list[ItemBlock]

@dataclass
class Article:
    number: int
    kind: Literal["temporary", "default"]

    paragraphs: list[Paragraph]

@dataclass
class Title:
    name: str
    articles: list[Article]

@dataclass
class Chapter:
    number: int
    name: str | None

    titles: list[Title]

@dataclass
class Document:
    title: str
    chapters: list[Chapter]

    def as_dict(self):
        return asdict(self)
