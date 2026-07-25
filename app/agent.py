from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from app.router import Router
from app.orchestrator import Orchestrator
from app.formatter import Formatter
from app.tools import ToolResult
from dataclasses import dataclass, asdict

@dataclass
class Trace:
    query: str
    selected_tool: str

    rewritten_query: str
    tool_result: ToolResult

    response: str

    def as_dict(self):
        return asdict(self)

class Agent:
    def __init__(self,
                 model_name: str,
                 model_quantization_config: BitsAndBytesConfig
                 ) -> None:

        self.model_name = model_name
        self.model_quantization_config = model_quantization_config

        self.model = AutoModelForCausalLM.from_pretrained(model_name,
                                                          quantization_config=model_quantization_config,
                                                            device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.router = Router(model=self.model,
                             tokenizer=self.tokenizer)
        self.orchestrator = Orchestrator(model=self.model,
                                         tokenizer=self.tokenizer)
        self.formatter = Formatter(model=self.model,
                                   tokenizer=self.tokenizer)

    def enter_query(self, query: str) -> str:
        tool_call = self.router.select_tool(query=query)
        tool_result = self.orchestrator.call_tool(query=query,
                                                  tool_call=tool_call)[0]
        response = self.formatter.format_tool_result(tool_result=tool_result,
                                                             query=query)
        return response

    def test_query(self, query: str) -> Trace:
        tool_call = self.router.select_tool(query=query)
        tool_result, rewritten_query = self.orchestrator.call_tool(query=query,
                                                                   tool_call=tool_call)
        response = self.formatter.format_tool_result(tool_result=tool_result,
                                                     query=query)
        return Trace(
            query=query,
            selected_tool=tool_call["tool"],
            rewritten_query=rewritten_query,
            tool_result=tool_result,
            response=response
        )
