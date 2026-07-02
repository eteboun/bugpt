from typing import ClassVar
from app.services import MenuService, RegulationService, Service

class Orchestrator:

    SERVICE_MAPPINGS: ClassVar[dict[str, Service]] = {
        "menu_service": MenuService(),
        "regulation_service": RegulationService(),
    }

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def call_service(self, service_call: dict, user_prompt: str):

        called_service = service_call["service"]

        service = self.SERVICE_MAPPINGS.get(called_service)
        if service is None:
            return None

        return service.call_tool(user_prompt=user_prompt)

