from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from ai.orchestrator import Orchestrator
from ai.formatter import Formatter
from ai.router import Router
import torch

class Agent:
    def __init__(self,
                 model_name: str,
                 model_quantization_config: BitsAndBytesConfig
                 ) -> None:

        self.model_name = model_name
        self.model_quantization_config = model_quantization_config

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name,
                                                          quantization_config=model_quantization_config,
                                                          device_map="auto",
                                                          torch_dtype=torch.float16,
                                                          )

        self.router = Router(model=self.model, tokenizer=self.tokenizer)
        self.orchestrator = Orchestrator(model=self.model, tokenizer=self.tokenizer)
        self.formatter = Formatter(model=self.model, tokenizer=self.tokenizer)

    def enter_query(self, query: str) -> str:
        service_call = self.router.select_service(query=query)
        answer = self.orchestrator.call_service(selected_service=service_call["service"], query=query)
        response = self.formatter.format_answer(answer=answer,
                                                query=query)
        return response

