from transformers import PreTrainedModel, PreTrainedTokenizer, TextStreamer
from pathlib import Path
from ai.model_runner import ModelRunner

class Formatter(ModelRunner):

    def __init__(self,
                 model: PreTrainedModel,
                 tokenizer: PreTrainedTokenizer,
                 streamer: TextStreamer = None
                 ) -> None:

        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)
        self.streamer = streamer

    def format_answer(self, query: str, answer) -> str:

        formatting_query = f"""
        User request: {query}\n
        Tool result: {answer}\n
        Answer:\n
        """

        formatted_result = self.run(query=formatting_query,
                                    system_prompt_file_name="formatter_system_prompt",
                                    max_new_tokens=500,
                                    streamer=self.streamer)

        return formatted_result