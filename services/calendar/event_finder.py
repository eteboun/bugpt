from models.calendar.calendar_models import Calendar
from cache.operations import read_cache
from config.calendar_config import CALENDAR_CACHE_NAME, CALENDAR_CACHE_FOLDER
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
from rapidfuzz import fuzz

class EventFinder:

    def __init__(self, model: SentenceTransformer) -> None:

        calendar_json = read_cache(
            cache_folder=CALENDAR_CACHE_FOLDER,
            cache_name=CALENDAR_CACHE_NAME,
        )

        self.model = model
        self.calendar = Calendar.deserialize(calendar_json)

    @staticmethod
    def _score_event(query: str, event_name: str) -> float:
        query = query.casefold()
        event_name = event_name.casefold()

        fuzzy_score = fuzz.ratio(query, event_name)

        query_tokens = set(query.split())
        event_tokens = set(event_name.split())

        token_coverage = len(query_tokens & event_tokens) / len(query_tokens)

        extra_token_count = len(event_tokens - query_tokens)

        coverage_bonus = token_coverage * 20
        length_penalty = extra_token_count * 2

        return fuzzy_score + coverage_bonus - length_penalty

    def find_event(self,
                   query: str,
                   fuzzy_threshold: float = 80,
                   semantic_threshold: float = 0.85
                   ) -> dict:

        ranked_events = sorted(
            self.calendar.events,
            key=lambda event: self._score_event(query, event.key.name),
            reverse=True,
        )

        top_event = ranked_events[0]
        print(f"fuzzy score: {self._score_event(query, top_event.key.name)}")
        if self._score_event(query, top_event.key.name) >= fuzzy_threshold:
            return top_event.serialize()

        query = f"query: {query}"
        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            convert_to_tensor=True,
        )

        embeddings = self.model.encode(
            [f"passage: {event}" for event in self.calendar.events],
            normalize_embeddings=True,
            convert_to_tensor=True,
        )

        scores = cos_sim(query_embedding, embeddings)[0]

        results = sorted(
            zip(self.calendar.events, scores.tolist()),
            key=lambda item: item[1],
            reverse=True,
        )
        top_score = results[0][1]
        found_event = results[0][0]
        print(f"semantic search score: {top_score}")
        if top_score >= semantic_threshold:
            return found_event.serialize()

        return {
            "status": "unsure"
        }