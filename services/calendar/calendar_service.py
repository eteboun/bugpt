from services.service import Service
from transformers import PreTrainedTokenizer, PreTrainedModel
from sentence_transformers import SentenceTransformer
from services.calendar.event_finder import EventFinder
from services.calendar.event_rewriter import EventRewriter

class CalendarService(Service):

    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer):
        super().__init__(generation_model, generation_tokenizer)

        self.event_finder = EventFinder(model=embedding_model)
        self.event_rewriter = EventRewriter()

    def _rewrite_event(self, event: str) -> str:
        return self.event_rewriter.rewrite_event(query=event)

    def _find_event(self, event: str) -> dict:
        return self.event_finder.find_event(query=event)

    def answer(self, query: str) -> dict:

        rewritten_query = self._rewrite_event(query)
        found_event = self._find_event(rewritten_query)
        return found_event