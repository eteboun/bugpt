from typing import ClassVar
import torch

class Formatter:

    system_prompt_path: ClassVar[str] = "system_prompts/formatter_system_prompt"

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        with open(self.system_prompt_path, 'r', encoding='utf8') as f:
            self.system_prompt = f.read()

    def format_tool_result(self, user_prompt: str, tool_result: dict) -> str:

        formatting_prompt = f"""
        User request: {user_prompt}\n
        Tool result: {tool_result}\n
        Answer:\n
        """

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            },
            {
                "role": "user",
                "content": formatting_prompt,
            }
        ]

        text = self.tokenizer.apply_chat_template(messages)
        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=500,
                do_sample=False,
            )

        input_len = inputs["input_ids"].shape[-1]
        generated_ids = outputs[0][input_len:]

        formatted_result = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return formatted_result