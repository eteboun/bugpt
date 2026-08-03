from sentence_transformers import SentenceTransformer
from transformers import PreTrainedModel, PreTrainedTokenizer

from services.service import Service
from services.regulation.query_rewriter import QueryRewriter
from services.regulation.doctype_classifier import DoctypeClassifier
from services.regulation.retriever import RegulationRetriever
from config.regulation_config import DOCUMENT_TYPES

class RegulationService(Service):

    def __init__(self,
                 generation_model: PreTrainedModel,
                 generation_tokenizer: PreTrainedTokenizer,
                 embedding_model: SentenceTransformer):
        super().__init__(generation_model, generation_tokenizer)

        self.query_rewriter = QueryRewriter(model=generation_model, tokenizer=generation_tokenizer)
        self.doctype_classifier = DoctypeClassifier(model=generation_model, tokenizer=generation_tokenizer)
        self.retriever = RegulationRetriever(model=embedding_model)

    def _rewrite_query(self, query: str) -> str:
        return self.query_rewriter.rewrite_query(query=query)

    def _classify_query(self, query: str) -> list[str]:
        doctypes = self.doctype_classifier.select_doctypes(query=query)

        return [
            doctype
            for doctype in doctypes
            if doctype in DOCUMENT_TYPES
        ]

    def answer(self, query: str) -> list[str]:

        query = self._rewrite_query(query)
        doctypes = self._classify_query(query)

        retrieval = self.retriever.retrieve(query=query,
                                            document_types=doctypes)

        return retrieval