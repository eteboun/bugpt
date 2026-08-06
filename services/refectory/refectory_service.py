from services.service import Service
from services.refectory.tool_selector import ToolSelector

class RefectoryService(Service):

    def __init__(self, model, tokenizer):
        super().__init__(model, tokenizer)
        self.tool_selector = ToolSelector()

    def answer(self, query: str) -> dict:
        print(self.tool_selector.run(query))
        return self.tool_selector.run(query)