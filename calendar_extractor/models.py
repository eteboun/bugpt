from dataclasses import dataclass
from datetime import date
from enum import Enum

@dataclass(frozen=True)
class EventKind(Enum):
    REGISTRATION = "Kayıt"
    ADMINISTRATIVE = "İdari"
    YADYOK = "YADYOK"
    EDUCATION = "Eğitim-Öğretim"
    APPLICATION = "Başvuru"

@dataclass(frozen=True)
class EventKey:
    name: str
    kind: EventKind

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind.value,
        }

@dataclass
class Event:
    key: EventKey
    start: date
    end: date

    def serialize(self) -> dict:
        return {
            "key": self.key.serialize(),
            "start": str(self.start),
            "end": str(self.end),
        }

@dataclass
class Calendar:
    start: date
    end: date
    events: list[Event]

    def serialize(self) -> dict:
        return {
            "start": str(self.start),
            "end": str(self.end),
            "events": [
                e.serialize() for e in self.events
            ]
        }