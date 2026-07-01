from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from router import Router
from orchestrator import Orchestrator

class Agent:
    def __init__(self,
                 control_model_name: str,
                 response_model_name: str,
                 response_model_quantization_config: BitsAndBytesConfig
                 ) -> None:

        self.control_model_name = control_model_name
        self.response_model_name = response_model_name
        self.response_model_quantization_config = response_model_quantization_config

        self.control_model = AutoModelForCausalLM.from_pretrained(control_model_name,
                                                                  device_map="auto")
        self.control_tokenizer = AutoTokenizer.from_pretrained(control_model_name)

        self.response_model = AutoModelForCausalLM.from_pretrained(response_model_name,
                                                                   device_map="auto",
                                                                   quantization_config=response_model_quantization_config)
        self.response_tokenizer = AutoTokenizer.from_pretrained(response_model_name)

        self.router = Router(model=self.control_model,
                             tokenizer=self.control_tokenizer,)
        self.orchestrator = Orchestrator()