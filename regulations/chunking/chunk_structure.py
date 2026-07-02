from dataclasses import dataclass, field, asdict
from typing import Literal, TypeAlias

@dataclass
class ItemIncluded:
    label: str
    item_block_number: int
    local_item_number: int
    general_item_number: int
    sub_item_number: int | None

@dataclass
class TableIncluded:
    table_number: int
    item_block_number: int

@dataclass
class BasePayload:

    text: str
    paragraph_number: int
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
class ListedPayload(BasePayload):
    content: list[ItemIncluded]
    kind: Literal["listed"] = "listed"

@dataclass
class TabularPayload(BasePayload):
    content: TableIncluded
    kind: Literal["tabular"] = "tabular"

@dataclass
class EmptyPayload(BasePayload):
    content: None = None
    kind: Literal["empty"] = "empty"

Payload: TypeAlias = TabularPayload | ListedPayload | EmptyPayload

@dataclass
class Chunk:
    id: str
    payload: Payload
    embedding_text: str

    def as_dict(self):
        return asdict(self)