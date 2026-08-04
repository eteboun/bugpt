from services.service import Service
from transformers import PreTrainedTokenizer, PreTrainedModel
from sentence_transformers import SentenceTransformer
from services.calendar.event_detector import EventDetector
from services.calendar.event_finder import EventFinder

class CalendarService(Service):

    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer):
        super().__init__(generation_model, generation_tokenizer)

        self.event_detector = EventDetector(model=generation_model, tokenizer=generation_tokenizer)
        self.event_finder = EventFinder(model=embedding_model)

    def _rewrite_query(self, query: str) -> str:
        return self.event_detector.rewrite_query(query)

    def _find_event(self, event: str) -> dict:
        return self.event_finder.find_event(event=event)

    def answer(self, query: str) -> dict:

        rewritten_query = self._rewrite_query(query)
        found_event = self._find_event(rewritten_query)

        return found_event