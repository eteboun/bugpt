from models.calendar.calendar_models import Calendar
from cache.operations import read_cache
from config.calendar_config import CALENDAR_CACHE_NAME, CALENDAR_CACHE_FOLDER
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

class EventFinder:

    def __init__(self, model: SentenceTransformer) -> None:

        calendar_json = read_cache(
            cache_folder=CALENDAR_CACHE_FOLDER,
            cache_name=CALENDAR_CACHE_NAME,
        )

        self.model = model
        self.calendar = Calendar.deserialize(calendar_json)

    def find_event(self, event: str) -> dict:

        query = f"query: {event}"
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

        found_event = results[0][0]
        return found_event.serialize()