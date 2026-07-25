from typing import ClassVar
from app.query_rewriter import QueryRewriter
from app.tools import *

class Orchestrator:

    TOOL_MAPPINGS: ClassVar[dict[str, Tool]] = {
        "unsure": UnsureTool(),
        "regulation_search": RegulationSearchTool(),
    }

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.query_rewriter = QueryRewriter(model, tokenizer)

    def call_tool(self, tool_call: dict, query: str):

        called_tool = tool_call["tool"]

        tool = self.TOOL_MAPPINGS.get(called_tool)
        if tool is None:
            return None

        rewritten_query = self.query_rewriter.rewrite_query(query=query) if not called_tool == "unsure" else None
        return tool.call(query=rewritten_query), rewritten_query
