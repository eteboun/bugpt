from typing import ClassVar
from menu.menu_tools import MenuTools
from regulations.regulation_tools import RegulationTools
import torch
import json

class Service:

    tools: ClassVar[dict]
    system_prompt_path: ClassVar[str]

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        with open(self.system_prompt_path, 'r', encoding='utf8') as f:
            self.system_prompt = f.read()

    def call_tool(self, user_prompt: str):

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            }
        ]

        text = self.tokenizer.apply_chat_template(messages)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False,
            )

        input_len = inputs["input_ids"].shape[-1]
        generated_ids = outputs[0][input_len:]

        generated = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        tool_call = json.loads(generated)

        called_tool = tool_call["tool_call"]
        if tool := self.tools.get(called_tool):
            args = tool_call["args"]
            result = tool(**args)

            return result

        return None

class MenuService(Service):

    tools = {
        "menu": MenuTools.tool_menu
    }

    system_prompt_path = "system_prompts/menu_service_system_prompt"

class RegulationService(Service):

    tools = {
        "search_regulation": RegulationTools.tool_search_regulation
    }

    system_prompt_path = "system_prompts/menu_service_system_prompt"
