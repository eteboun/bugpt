from dataclasses import dataclass, field, asdict

@dataclass
class ItemIncluded:
    item_letter: str
    sub_item_number: int | None

    def as_dict(self):
        return asdict(self)

@dataclass
class Payload:
    text: str
    paragraph_number: int
    items_included: list[ItemIncluded]

    main_title: str = field(init=False)
    chapter_name: str = field(init=False)
    chapter_number: int = field(init=False)
    article_title: str = field(init=False)
    article_number: int = field(init=False)
    id: str = field(init=False)

    def as_dict(self):
        return asdict(self)

@dataclass
class Chunk:
    id: str
    payload: Payload
    embedding_text: str

    def as_dict(self):
        return asdict(self)