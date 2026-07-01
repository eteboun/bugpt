from typing import ClassVar
from pathlib import Path

class ModelRunner:

    system_prompt_file_name: ClassVar[str]

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

        path = Path(__file__).resolve().parent / "system_prompts" / self.system_prompt_file_name

        with open(path, 'r', encoding='utf-8') as f:
            self.system_prompt = f.read()