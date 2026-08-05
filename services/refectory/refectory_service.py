from services.service import Service
from services.refectory.tool_selector import ToolSelector
from config.refectory_config import MENU_CACHE_NAME, MENU_PRICE_CACHE_NAME, REFECTORY_CACHE_FOLDER
from cache.operations import read_cache
from typing import ClassVar

class RefectoryService(Service):

    TOOL_CACHE_NAME_MAPPING: ClassVar[dict[str, str]] = {
        'menu': MENU_CACHE_NAME,
        'menu_price': MENU_PRICE_CACHE_NAME,
    }

    def __init__(self, model, tokenizer):
        super().__init__(model, tokenizer)
        self.tool_selector = ToolSelector()

    def answer(self, query: str):

        tool_call = self.tool_selector.select(query=query)
        tool = tool_call['tool']

        if tool not in self.TOOL_CACHE_NAME_MAPPING:
            return []

        cache_name = self.TOOL_CACHE_NAME_MAPPING[tool]
        return read_cache(
            cache_folder=REFECTORY_CACHE_FOLDER,
            cache_name=cache_name,
        )