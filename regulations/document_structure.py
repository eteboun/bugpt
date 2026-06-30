from dataclasses import dataclass
from typing import Literal

@dataclass
class SubItem:
    text: str
    local_index: int

@dataclass
class Item:
    text: str
    label: str | None
    local_index: int

    sub_items: list[SubItem]

@dataclass
class ItemGroup:
    items: list[Item]
    ending: str | None

    local_index: int

@dataclass
class Paragraph:
    number: int
    text: str

    item_groups: list[ItemGroup]

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