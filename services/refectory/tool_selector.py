from ai.model_runner import ModelRunner
from pathlib import Path

class ToolSelector(ModelRunner):

    def __init__(self, model, tokenizer):
        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)

    def select_tool(self, query: str) -> dict[str, str]:

        tool = self.run(
            system_prompt_file_name="refectory_system_prompt",
            query=query,
            max_new_tokens=100
        )

        return {"tool": tool.strip()}