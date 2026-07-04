from dataclasses import dataclass, field, asdict
from typing import Literal, TypeAlias
from regulations.models import Item

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
class BasePayload:

    text: str
    paragraph_number: int = field(init=False)
    main_title: str = field(init=False)
    chapter_name: str = field(init=False)
    chapter_number: int = field(init=False)
    article_title: str = field(init=False)
    article_number: int = field(init=False)
    article_kind: Literal["temporary", "default"] = field(init=False)
    id: str = field(init=False)

    def as_dict(self):
        return asdict(self)

@dataclass
class ItemPayload(BasePayload):
    content: list[ItemIncluded]
    kind: Literal["item"] = "item"

@dataclass
class TablePayload(BasePayload):
    content: TableIncluded
    kind: Literal["table"] = "table"

@dataclass
class EmptyPayload(BasePayload):
    content: None = None
    kind: Literal["empty"] = "empty"

Payload: TypeAlias = TablePayload | ItemPayload | EmptyPayload

@dataclass
class Chunk:
    id: str
    payload: Payload
    embedding_text: str

    def as_dict(self):
        return asdict(self)