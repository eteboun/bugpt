from services.regulation.regulation_service import RegulationService
from services.unsure.unsure_service import UnsureService

class Orchestrator:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        self.services = {
            "regulation": RegulationService(model, tokenizer),
            "unsure": UnsureService(model, tokenizer),
        }


    def call_service(self, selected_service: str, query: str):

        service = self.services.get(selected_service)
        if service is None:
            return None

        return service.answer(query)