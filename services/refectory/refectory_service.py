from services.service import Service
from services.refectory.tool_selector import ToolSelector
from config.cache_names import MENU_CALENDAR_CACHE_NAME, MENU_PRICE_CACHE_NAME, REFECTORY_CACHE_FOLDER
from cache.operations import read_cache
from schemas.refectory.menu_calendar_models import MenuFilter, MenuCalendar
from typing import ClassVar
from datetime import date

def tool_menu(filter_: MenuFilter) -> dict:

    menu_calendar_json = read_cache(
        cache_folder=REFECTORY_CACHE_FOLDER,
        cache_name=MENU_CALENDAR_CACHE_NAME
    )
    menu_calendar = MenuCalendar.deserialize(menu_calendar_json)
    menu = menu_calendar.search(date_=date.today())

    filtered_menu = menu.filter(filter_)
    return filtered_menu.serialize()

def tool_menu_price() -> dict:
    return read_cache(
        cache_folder=REFECTORY_CACHE_FOLDER,
        cache_name=MENU_PRICE_CACHE_NAME
    )

class RefectoryService(Service):

    TOOLS: ClassVar[dict] = {
        "menu": tool_menu,
        "menu_price": tool_menu_price
    }

    def __init__(self, model, tokenizer):
        super().__init__(model, tokenizer)
        self.tool_selector = ToolSelector()

    def answer(self, query: str) -> dict:
        tool_call = self.tool_selector.run(
            query=query,
        )

        tool_name = tool_call['tool']
        tool = self.TOOLS[tool_name]
        args = tool_call['args']

        return tool(**args)