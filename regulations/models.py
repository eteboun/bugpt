from dataclasses import dataclass, asdict, field
from typing import Literal

@dataclass
class SubItem:
    text: str
    label: str | None
    local_index: int

@dataclass
class Item:
    text: str
    label: str | None
    general_index: int

    sub_items: list[SubItem]
    ending: str | None = None

@dataclass
class Row:
    content: list[str]
    local_index: int

@dataclass
class Table:
    row_titles: list[str]
    rows: list[Row]
    general_index: int
    local_index: int

@dataclass
class ParagraphContent:
    items: list[Item] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)

@dataclass
class Paragraph:
    number: int
    text: str

    content: ParagraphContent

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

    name: str
    chapters: list[Chapter]

    document_type: str = field(init=False)

    def as_dict(self):
        return asdict(self)
