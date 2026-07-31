from functools import wraps
from typing import ClassVar
from pathlib import Path
import shutil
import torch
import qdrant_client.models as models

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from regulations.pipeline import Pipeline

class DatabaseManager:

    VECTOR_MODEL: ClassVar[SentenceTransformer] = SentenceTransformer("intfloat/multilingual-e5-base",
                                                                      model_kwargs={"torch_dtype": torch.float16},
                                                                      device="cuda")

    BM25_MODEL_NAME: ClassVar[str] = "Qdrant/bm25"

    BM25_OPTIONS: ClassVar[dict] = {
        "language": "turkish",
        "tokenizer": "word",
    }


    COLLECTION: ClassVar[str] = "regulations"
    DB_NAME: ClassVar[str] = "storage"

    @staticmethod
    def _run_client(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            path = Path(__file__).resolve().parent / DatabaseManager.DB_NAME
            client = QdrantClient(path=str(path))
            try:
                return func(client, *args, **kwargs)
            finally:
                client.close()

        return wrapper

    @staticmethod
    @_run_client
    def _build_db(client: QdrantClient, use_cache: bool = True):

        for document_type in Pipeline.DOCUMENT_TYPE_MAPPING.keys():
            pipeline = Pipeline(document_type, DatabaseManager.COLLECTION, use_cache)
            DatabaseManager._save_pipeline_chunks(pipeline=pipeline, client=client)

    @staticmethod
    def _delete_db():
        path = Path(__file__).resolve().parent / DatabaseManager.DB_NAME
        if path.exists():
            shutil.rmtree(path)
        else:
            raise Exception("Path doesn't exist")

    @staticmethod
    def _save_pipeline_chunks(pipeline: Pipeline, client: QdrantClient) -> None:

        chunks = pipeline.run()

        if not client.collection_exists(DatabaseManager.COLLECTION):

            client.create_collection(
                collection_name=DatabaseManager.COLLECTION,
                vectors_config={
                    "dense": models.VectorParams(
                            size=DatabaseManager.VECTOR_MODEL.get_embedding_dimension(),
                            distance=models.Distance.COSINE
                        )
                },
                sparse_vectors_config={
                    "bm25": models.SparseVectorParams(
                        modifier=models.Modifier.IDF
                    )
                }
            )

        points = [
            models.PointStruct(
                id=chunk.id,
                vector={
                    "dense": DatabaseManager.VECTOR_MODEL.encode(f"passage: {chunk.payload.embedding_text}",
                                                                 normalize_embeddings=True).tolist(),

                    "bm25": models.Document(
                        text=chunk.payload.embedding_text,
                        model=DatabaseManager.BM25_MODEL_NAME,
                        options=DatabaseManager.BM25_OPTIONS,
                    )
                },
                payload=chunk.payload.as_dict()
            ) for chunk in chunks
        ]

        client.upsert(
            collection_name=DatabaseManager.COLLECTION,
            points=points
        )

    @staticmethod
    def rebuild_db(use_cache: bool = True):
        DatabaseManager._delete_db()
        DatabaseManager._build_db(use_cache=use_cache)

    @staticmethod
    @_run_client
    def search_chunk(client: QdrantClient,
                     query: str,
                     document_types: list[str],
                     search_limit: int = 2,
                     ) -> list[str]:

        if not document_types or search_limit <= 0:
            return []

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

        vector = DatabaseManager.VECTOR_MODEL.encode(
            f"query: {query}"
        ).tolist()

        points = client.query_points(
            collection_name=DatabaseManager.COLLECTION,

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
                        model=DatabaseManager.BM25_MODEL_NAME,
                        options=DatabaseManager.BM25_OPTIONS
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

DatabaseManager.rebuild_db(use_cache=True)
