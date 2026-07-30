class Service:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def answer(self, query: str):
        ...