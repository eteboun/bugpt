from dataclasses import dataclass, field, asdict
from typing import Literal
from models.regulation.document_models import Item

@dataclass
class FlattenedSubItem:
    text: str
    label: str | None
    sub_item_number: int

@dataclass
class FlattenedItem:
    text: str
    label: str | None

    item_number: int
    included_sub_items: list[FlattenedSubItem]

@dataclass
class ItemGroup:
    items: list[Item]
    include_paragraph_text: bool

@dataclass
class FlattenedItemGroup:
    items: list[FlattenedItem]
    include_paragraph_text: bool

@dataclass
class ChunkedItem:
    text: str
    flattened_items: list[FlattenedItem]

@dataclass
class ChunkedItemGroup:
    items: list[ChunkedItem]
    consumed_paragraph_text: bool

@dataclass
class SubItemIncluded:
    label: str | None
    sub_item_number: int

@dataclass
class ItemIncluded:
    label: str | None
    item_number: int
    included_sub_items: list[SubItemIncluded]

@dataclass
class TableIncluded:
    table_number: int

@dataclass
class Payload:

    kind: Literal["item", "table", "paragraph"]


    text: str
    content: list[ItemIncluded] | TableIncluded | None

    document_type: str = field(init=False)
    document_name: str = field(init=False)
    chapter_name: str = field(init=False)
    chapter_number: int = field(init=False)
    article_title: str = field(init=False)
    article_number: int = field(init=False)
    paragraph_number: int = field(init=False)
    article_kind: Literal["temporary", "default"] = field(init=False)

    id: str = field(init=False)
    embedding_text: str = field(init=False)

    def as_dict(self):
        return asdict(self)

@dataclass
class Chunk:
    id: str
    payload: Payload

    def as_dict(self):
        return asdict(self)