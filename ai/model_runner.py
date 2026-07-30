from pathlib import Path
import torch

class ModelRunner:

    def __init__(self, model, tokenizer, sys_prompts_dir: Path):
        self.model = model
        self.tokenizer = tokenizer
        self.system_prompts_dir = sys_prompts_dir

    def run(self,
            system_prompt_file_name: str,
            query: str,
            max_new_tokens: int = 100
            ) -> str:

        if self.model is None or self.tokenizer is None:
            raise Exception('Model and Tokenizer are not initialized')

        path = self.system_prompts_dir / system_prompt_file_name

        if not path.exists():
            raise FileNotFoundError(f"File {path} not found")

        system_prompt = path.read_text(encoding='utf-8')

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            }
        ]

        text = self.tokenizer.apply_chat_template(messages,
                                                  tokenize=False,
                                                  add_generation_prompt=True,
                                                  enable_thinking=False)

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        input_len = inputs["input_ids"].shape[-1]
        generated_ids = outputs[0][input_len:]

        generated = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return generated