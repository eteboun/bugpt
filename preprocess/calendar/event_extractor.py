import requests
from config.cache_names import ACADEMIC_CALENDAR_CACHE_NAME, ACADEMIC_CALENDAR_CACHE_FOLDER
from datetime import date, timedelta
from typing import ClassVar
from bs4 import BeautifulSoup, Tag
from schemas.calendar.calendar_models import Event, EventKey, EventKind, Calendar
from cache.operations import write_cache

today = date.today()

class EventExtractor:

    BASE_URL: ClassVar[str] = "https://akademiktakvim.bogazici.edu.tr/tr/events/akademik?Date="

    EVENT_LIST_CLASS: ClassVar[str] = "events-list-spec"
    EVENT_NAME_CLASS: ClassVar[str] = "title query-title"
    EVENT_KIND_CLASS: ClassVar[str] = "tag query-tag"
    EVENT_HTML_ELEMENT: ClassVar[str] = "li"

    START_DATE: ClassVar[date] = today
    END_DATE: ClassVar[date] = today + timedelta(days=364)

    def __init__(self):
        self.soup = None

    @staticmethod
    def _get_url(date_: date) -> str:
        return EventExtractor.BASE_URL + str(date_)

    @staticmethod
    def _get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    def _extract_event_tag_list(date_: date) -> Tag | None:

        url = EventExtractor._get_url(date_)
        soup = EventExtractor._get_soup(url)

        event_tag_list = soup.find(class_=EventExtractor.EVENT_LIST_CLASS)
        return event_tag_list

    @staticmethod
    def _extract_event_tags(event_tag_list: Tag | None) -> list[Tag]:
        if not event_tag_list:
            return []

        event_tags = event_tag_list.find_all(EventExtractor.EVENT_HTML_ELEMENT, recursive=False)
        return event_tags

    @staticmethod
    def _extract_event_key(event_tag: Tag) -> EventKey:
        name_tag = event_tag.find(class_=EventExtractor.EVENT_NAME_CLASS)
        kind_tag = event_tag.find(class_=EventExtractor.EVENT_KIND_CLASS)

        if not name_tag or not kind_tag:
            raise ValueError(f"Invalid event: {name_tag} {kind_tag}")

        return EventKey(
            name=name_tag.string.strip(),
            kind=EventKind(kind_tag.string.strip()),
        )

    @staticmethod
    def _get_new_ongoing_events(
            ongoing_events: dict[EventKey, date],
            event_keys: set[EventKey],
            date_: date,
    ) -> dict[EventKey, date]:

        return {
            event_key: ongoing_events.get(event_key, date_)
            for event_key in event_keys
        }

    @staticmethod
    def _get_finished_events(
            ongoing_events: dict[EventKey, date],
            event_keys: set[EventKey],
    ) -> dict[EventKey, date]:

        return {
            ongoing_event: ongoing_events.get(ongoing_event)
            for ongoing_event in ongoing_events
            if ongoing_event not in event_keys
        }

    @staticmethod
    def _extract_calendar() -> Calendar:

        events = []

        date_ = EventExtractor.START_DATE
        ongoing_events: dict[EventKey, date] = {}

        while date_ <= EventExtractor.END_DATE or ongoing_events:

            event_tag_list = EventExtractor._extract_event_tag_list(date_)
            event_tags = EventExtractor._extract_event_tags(event_tag_list)

            event_keys = {
                EventExtractor._extract_event_key(event_tag) for event_tag in event_tags
            }

            finished_events = EventExtractor._get_finished_events(
                ongoing_events=ongoing_events,
                event_keys=event_keys,
            )

            for finished_event in finished_events:
                events.append(Event(
                    key=finished_event,
                    start=finished_events[finished_event],
                    end=date_ - timedelta(days=1),
                ))

                ongoing_events.pop(finished_event)

            ongoing_events = EventExtractor._get_new_ongoing_events(
                ongoing_events=ongoing_events,
                event_keys=event_keys,
                date_=date_,
            )

            date_ += timedelta(days=1)

        return Calendar(
            start=EventExtractor.START_DATE,
            end=date_ - timedelta(days=1),
            events=events,
        )

    @staticmethod
    def _serialize_calendar(calendar: Calendar) -> dict:
        return calendar.serialize()

    @staticmethod
    def cache():
        calendar = EventExtractor._extract_calendar()
        serialized_calendar = calendar.serialize()

        write_cache(
            cache_folder=ACADEMIC_CALENDAR_CACHE_FOLDER,
            cache_name=ACADEMIC_CALENDAR_CACHE_NAME,
            cache_data=serialized_calendar
        )

EventExtractor.cache()