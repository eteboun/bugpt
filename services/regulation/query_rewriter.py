from pathlib import Path
from ai.model_runner import ModelRunner

class QueryRewriter(ModelRunner):

    def __init__(self, model, tokenizer):
        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)

    def rewrite_query(self, query) -> str:

        new_query = self.run(query=query,
                             system_prompt_file_name="query_rewriter_system_prompt",
                             max_new_tokens=200)

        return new_query