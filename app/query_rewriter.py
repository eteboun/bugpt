from app.model_runner import ModelRunner
import torch

class QueryRewriter(ModelRunner):

    system_prompt_file_name = "query_rewriter_system_prompt"

    def rewrite_query(self, query):

        messages = [
            {
                "role": "system",
                "content": self.system_prompt,
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
                max_new_tokens=100,
                do_sample=False,
            )

        input_len = inputs["input_ids"].shape[-1]
        generated_ids = outputs[0][input_len:]

        new_query = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        print(new_query)
        return new_query