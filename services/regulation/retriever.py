from sentence_transformers import SentenceTransformer
from qdrant_client import models
from config.regulation_config import REGULATION_COLLECTION_NAME, REGULATION_DB_PATH
from config.model_config import BM25_MODEL_NAME, BM25_OPTIONS
from qdrant.client import run_client
from schemas.regulation.document_models import DocTypes

class RegulationRetriever:

    def __init__(self, model: SentenceTransformer):
        self.model = model

    def retrieve(self,
                 query: str,
                 document_types: list[DocTypes],
                 search_limit: int = 2,
                 ) -> list[str]:

        if not document_types or search_limit <= 0:
            return []

        with run_client(db_path=REGULATION_DB_PATH) as client:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_type",
                        match=models.MatchAny(
                            any=document_types
                        ),
                    )
                ]
            )

            prefetch_limit = max(10, search_limit)

            vector = self.model.encode(
                f"query: {query}"
            ).tolist()

            points = client.query_points(
                collection_name=REGULATION_COLLECTION_NAME,

                prefetch=[
                    models.Prefetch(
                        query=vector,
                        using="dense",
                        filter=query_filter,
                        limit=prefetch_limit
                    ),

                    models.Prefetch(
                        query=models.Document(
                            text=query,
                            model=BM25_MODEL_NAME,
                            options=BM25_OPTIONS
                        ),
                        using="bm25",
                        filter=query_filter,
                        limit=prefetch_limit
                    )
                ],
                query=models.FusionQuery(
                    fusion=models.Fusion.RRF
                ),
                limit=search_limit,
                with_payload=True
            ).points

            results = [
                point.payload.get("text") for point in points
            ]

        return results