from rapidfuzz import process
from pathlib import Path
from calendar_extractor.event_extractor import EventExtractor
from calendar_extractor.models import Calendar
import json

class EventFinder:

    def __init__(self) -> None:

        path = Path(__file__).resolve().parent / EventExtractor.SAVE_FILE_NAME
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found")

        with open(path, "r", encoding="utf-8") as f:
            calendar_json = json.load(f)

        self.calendar = Calendar.deserialize(calendar_json)
        self.event_names = {
            event.key.name for event in self.calendar.events
        }

    def find_event(self, event: str) -> list[dict]:

        match = process.extractOne(
            event,
            self.event_names,
            score_cutoff=90,
        )

        if not match:
            return []

        searched_event = match[0]

        return [
            event.serialize()
            for event in self.calendar.events
            if event.key.name == searched_event
        ]

ef = EventFinder()

print(ef.find_event("yatay geçiş başvuru dönemi"))

