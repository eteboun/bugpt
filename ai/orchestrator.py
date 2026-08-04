from services.calendar.calendar_service import CalendarService
from services.refectory.refectory_service import RefectoryService
from services.regulation.regulation_service import RegulationService
from services.unsure.unsure_service import UnsureService
from transformers import PreTrainedModel, PreTrainedTokenizer
from sentence_transformers import SentenceTransformer

class Orchestrator:

    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer):

        self.services = {
            "regulation": RegulationService(generation_model, generation_tokenizer, embedding_model),
            "refectory": RefectoryService(generation_model, generation_tokenizer),
            "calendar": CalendarService(generation_model, generation_tokenizer, embedding_model),
            "unsure": UnsureService(generation_model, generation_tokenizer),
        }

    def call_service(self, selected_service: str, query: str):

        service = self.services.get(selected_service)
        if service is None:
            return None

        return service.answer(query)