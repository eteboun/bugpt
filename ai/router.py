from pathlib import Path
from ai.model_runner import ModelRunner

class Router(ModelRunner):

    def __init__(self, model, tokenizer):
        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)

    def select_service(self, query: str) -> dict:

        service = self.run(query=query,
                           system_prompt_file_name="router_system_prompt",
                           max_new_tokens=100)

        return {"service": service.strip()}
