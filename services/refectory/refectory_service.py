from services.service import Service
from services.refectory.tool_selector import ToolSelector
from refectory_extractor.menu_extractor import MenuExtractor
from refectory_extractor.menu_price_extractor import MenuPriceExtractor

from typing import ClassVar, TypeAlias

Extractor: TypeAlias = type[MenuExtractor] | type[MenuPriceExtractor]

class RefectoryService(Service):

    TOOLS: ClassVar[dict[str, Extractor]] = {
        'menu': MenuExtractor,
        'menu_price': MenuPriceExtractor,
    }

    def __init__(self, model, tokenizer):
        super().__init__(model, tokenizer)
        self.tool_selector = ToolSelector(model=model, tokenizer=tokenizer)

    def answer(self, query: str):

        tool_call = self.tool_selector.select_tool(query=query)
        tool = tool_call['tool']

        if tool not in self.TOOLS:
            return []

        tool = self.TOOLS[tool]
        result = tool.call()

        return result