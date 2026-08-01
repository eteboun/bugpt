from services.service import Service
from services.regulation.query_rewriter import QueryRewriter
from services.regulation.doctype_classifier import DoctypeClassifier
from regulation_rag.database_manager import DatabaseManager
from typing import ClassVar

class RegulationService(Service):

    DOCUMENT_TYPES: ClassVar[set] = {"dormitory", "erasmus",
                                     "undergraduate", "graduate",
                                     "major", "minor"}

    def __init__(self, model, tokenizer):
        super().__init__(model, tokenizer)

        self.query_rewriter = QueryRewriter(model=model, tokenizer=tokenizer)
        self.doctype_classifier = DoctypeClassifier(model=model, tokenizer=tokenizer)

    def _rewrite_query(self, query: str) -> str:
        return self.query_rewriter.rewrite_query(query=query)

    def _classify_query(self, query: str) -> list[str]:
        doctypes = self.doctype_classifier.select_doctypes(query=query)

        return [
            doctype
            for doctype in doctypes
            if doctype in self.DOCUMENT_TYPES
        ]

    def answer(self, query: str) -> list[str]:

        query = self._rewrite_query(query)
        doctypes = self._classify_query(query)

        retrieval = DatabaseManager.search_chunk(query=query,
                                                 document_types=doctypes)

        return retrieval