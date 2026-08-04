from transformers import PreTrainedModel, PreTrainedTokenizer
from sentence_transformers import SentenceTransformer
from ai.orchestrator import Orchestrator
from ai.formatter import Formatter
from ai.router import Router

class Agent:
    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer) -> None:

        self.generation_tokenizer = generation_tokenizer
        self.generation_model = generation_model

        self.router = Router(model=generation_model, tokenizer=generation_tokenizer)
        self.orchestrator = Orchestrator(generation_model=generation_model,
                                         generation_tokenizer=generation_tokenizer,
                                         embedding_model=embedding_model)
        self.formatter = Formatter(model=generation_model, tokenizer=generation_tokenizer)

    def enter_query(self, query: str) -> str:
        service_call = self.router.select_service(query=query)
        answer = self.orchestrator.call_service(selected_service=service_call["service"], query=query)
        response = self.formatter.format_answer(answer=answer,
                                                query=query)
        return response