from pathlib import Path
from ai.model_runner import ModelRunner

class Formatter(ModelRunner):

    def __init__(self, model, tokenizer):
        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)

    def format_answer(self, query: str, answer) -> str:

        formatting_query = f"""
        User request: {query}\n
        Tool result: {answer}\n
        Answer:\n
        """

        formatted_result = self.run(query=formatting_query,
                                    system_prompt_file_name="formatter_system_prompt",
                                    max_new_tokens=500)

        return formatted_result