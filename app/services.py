from typing import override
from abc import ABC, abstractmethod

from menu.menu_tools import MenuTools
from regulations.regulation_tools import RegulationTools

class Service(ABC):
    @abstractmethod
    def call_tool(self, user_prompt: str) -> object:
        ...

class MenuService(Service):

    @override
    def call_tool(self, user_prompt: str) -> object:
        return MenuTools.tool_menu()

class RegulationService(Service):

    @override
    def call_tool(self, user_prompt: str) -> object:
        return RegulationTools.tool_search_regulation(query=user_prompt)