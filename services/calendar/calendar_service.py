from services.service import Service
from transformers import PreTrainedTokenizer, PreTrainedModel
from sentence_transformers import SentenceTransformer
from services.calendar.event_finder import EventFinder
from services.calendar.query_rewriter import QueryRewriter

class CalendarService(Service):

    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer):
        super().__init__(generation_model, generation_tokenizer)

        self.event_finder = EventFinder(model=embedding_model)
        self.query_rewriter = QueryRewriter()

    def answer(self, query: str) -> dict:

        rewritten_query = self.query_rewriter.rewrite_query(query)
        found_event = self.event_finder.find_event(rewritten_query)
        return found_event