from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from app.router import Router
from app.orchestrator import Orchestrator
from app.formatter import Formatter

class Agent:
    def __init__(self,
                 model_name: str,
                 model_quantization_config: BitsAndBytesConfig
                 ) -> None:

        self.model_name = model_name
        self.model_quantization_config = model_quantization_config

        self.model = AutoModelForCausalLM.from_pretrained(model_name,
                                                            device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.router = Router(model=self.model,
                             tokenizer=self.tokenizer)
        self.orchestrator = Orchestrator(model=self.model,
                                         tokenizer=self.tokenizer)
        self.formatter = Formatter(model=self.model,
                                   tokenizer=self.tokenizer)
    def enter_prompt(self, user_prompt: str) -> str:
        service_call = self.router.select_service(user_prompt=user_prompt)
        tool_result = self.orchestrator.call_service(user_prompt=user_prompt,
                                                     service_call=service_call)
        response = self.formatter.format_tool_result(tool_result=tool_result,
                                                             user_prompt=user_prompt)
        return response