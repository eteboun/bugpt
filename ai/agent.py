from transformers import PreTrainedModel, PreTrainedTokenizer
from ai.orchestrator import Orchestrator
from ai.formatter import Formatter
from ai.router import Router

class Agent:
    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer,
                 ) -> None:

        self.tokenizer = tokenizer
        self.model = model

        self.router = Router(model=model, tokenizer=tokenizer)
        self.orchestrator = Orchestrator(model=model, tokenizer=tokenizer)
        self.formatter = Formatter(model=model, tokenizer=tokenizer)

    def enter_query(self, query: str) -> str:
        service_call = self.router.select_service(query=query)
        answer = self.orchestrator.call_service(selected_service=service_call["service"], query=query)
        response = self.formatter.format_answer(answer=answer,
                                                query=query)
        return response