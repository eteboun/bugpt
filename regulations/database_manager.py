from functools import wraps
from typing import ClassVar
from pathlib import Path
import shutil
import torch

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

from regulations.pipeline import Pipeline

class DatabaseManager:

    MODEL: ClassVar[SentenceTransformer] = SentenceTransformer("intfloat/multilingual-e5-base",
                                                               model_kwargs={"torch_dtype": torch.float16},
                                                               device="cuda")
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
    def build_db(client: QdrantClient, use_cache: bool = True):

        for pipeline_name in Pipeline.PIPELINE_NAME_MAPPING.keys():
            pipeline = Pipeline(pipeline_name, DatabaseManager.COLLECTION, use_cache)
            DatabaseManager._save_pipeline_chunks(pipeline=pipeline, client=client)

    @staticmethod
    def rebuild_db(use_cache: bool = True):
        DatabaseManager.delete_db()
        DatabaseManager.build_db(use_cache=use_cache)

    @staticmethod
    def delete_db():
        path = Path(__file__).resolve().parent / DatabaseManager.DB_NAME
        if path.exists():
            shutil.rmtree(path)
        else:
            raise Exception("Path doesn't exist")

    @staticmethod
    @_run_client
    def search_chunk(client: QdrantClient, query: str, limit: int = 2) -> list[dict]:

        query = f"query: {query}"
        vector = DatabaseManager.MODEL.encode(query).tolist()

        results = client.query_points(
            collection_name=DatabaseManager.COLLECTION,
            query=vector,
            limit=limit,
        ).points

        result = []
        for point in results:

            result.append({
                "score": round(point.score, 3),
                "text": point.payload.get("text")
            })

        return result

    @staticmethod
    def _save_pipeline_chunks(pipeline: Pipeline, client: QdrantClient) -> None:

        chunks = pipeline.run()

        if not client.collection_exists(DatabaseManager.COLLECTION):

            client.create_collection(
                collection_name=DatabaseManager.COLLECTION,
                vectors_config=VectorParams(
                    size=DatabaseManager.MODEL.get_embedding_dimension(),
                    distance=Distance.COSINE
                )
            )

        points = [
            PointStruct(
                id=chunk.id,
                vector=DatabaseManager.MODEL.encode(chunk.embedding_text).tolist(),
                payload=chunk.payload.as_dict()
            ) for chunk in chunks
        ]

        client.upsert(
            collection_name=DatabaseManager.COLLECTION,
            points=points
        )

DatabaseManager.rebuild_db(use_cache=True)