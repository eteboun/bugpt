from typing import override, Any
from abc import ABC, abstractmethod

from regulations.database_manager import DatabaseManager

ToolResult = dict[str, Any]

class Tool(ABC):
    @abstractmethod
    def call(self, query: str) -> ToolResult:
        ...

class UnsureTool(Tool):

    @override
    def call(self, query: str) -> ToolResult:
        return {"status": "unsure"}

class RegulationSearchTool(Tool):

    @override
    def call(self, query: str) -> ToolResult:
        return {
            "status": "success",
            "result": DatabaseManager.search_chunk(query=query)
        }
