import torch
import json
from typing import ClassVar

class Router:

    system_prompt_path: ClassVar[str] = "system_prompts/router_system_prompt"

    def __init__(self, model, tokenizer):

        self.model = model
        self.tokenizer = tokenizer

        with open(self.system_prompt_path) as f:
            self.system_prompt = f.read()

    def select_service(self, user_prompt: str) -> dict:

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
        return json.loads(generated)