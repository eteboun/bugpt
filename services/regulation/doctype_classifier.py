from ai.model_runner import ModelRunner
from pathlib import Path
import json

class DoctypeClassifier(ModelRunner):

    def __init__(self, model, tokenizer):
        sys_prompt_dir = Path(__file__).resolve().parent / "system_prompts"
        super().__init__(model, tokenizer, sys_prompt_dir)

    def select_doctypes(self, query: str) -> list[str]:

        selected_doctypes = self.run(system_prompt_file_name="doctype_classifier_system_prompt",
                                     query=query)
        selected_doctypes = json.loads(selected_doctypes)["selected_doctypes"]
        print(f"selected_doctypes: {selected_doctypes}")
        return selected_doctypes