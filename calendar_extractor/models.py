from calendar import Calendar
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

    @classmethod
    def deserialize(cls, data: dict) -> "EventKey":

        name = data["name"]
        kind = EventKind(data["kind"])

        return cls(
            name=name,
            kind=kind
        )

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

    @classmethod
    def deserialize(cls, data: dict) -> "Event":

        start = date.fromisoformat(data["start"])
        end = date.fromisoformat(data["end"])
        key = EventKey.deserialize(data["key"])

        return cls(
            key=key,
            start=start,
            end=end
        )

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

    @classmethod
    def deserialize(cls, data: dict) -> "Calendar":

        start = date.fromisoformat(data["start"])
        end = date.fromisoformat(data["end"])
        events = [Event.deserialize(e) for e in data["events"]]

        return cls(
            start=start,
            end=end,
            events=events
        )