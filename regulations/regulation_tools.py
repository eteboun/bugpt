from functools import wraps
from typing import ClassVar
from pathlib import Path
import shutil
import torch

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from regulations.pipelines import (dormitory_pipeline,
                                   erasmus_pipeline,
                                   major_pipeline,
                                   undergraduate_pipeline,
                                   graduate_pipeline)

class RegulationTools:

    MODEL: ClassVar[SentenceTransformer] = SentenceTransformer("intfloat/multilingual-e5-base",
                                                               model_kwargs={"torch_dtype": torch.float16},
                                                               device="cuda")
    COLLECTION: ClassVar[str] = "regulations"

    DB_NAME: ClassVar[str] = "storage"

    @staticmethod
    def _run_client(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            path = Path(__file__).resolve().parent / RegulationTools.DB_NAME
            client = QdrantClient(path=str(path))
            try:
                return func(client, *args, **kwargs)
            finally:
                client.close()

        return wrapper

    @staticmethod
    @_run_client
    def build_db(client: QdrantClient):

        dormitory_pipeline.run_pipeline(model=RegulationTools.MODEL, client=client)
        erasmus_pipeline.run_pipeline(model=RegulationTools.MODEL, client=client)
        major_pipeline.run_pipeline(model=RegulationTools.MODEL, client=client)
        undergraduate_pipeline.run_pipeline(model=RegulationTools.MODEL, client=client)
        graduate_pipeline.run_pipeline(model=RegulationTools.MODEL, client=client)

    @staticmethod
    def rebuild_db():
        RegulationTools.delete_db()
        RegulationTools.build_db()

    @staticmethod
    def delete_db():
        path = Path(__file__).resolve().parent / RegulationTools.DB_NAME
        if path.exists():
            shutil.rmtree(path)
        else:
            raise Exception("Path doesn't exist")

    @staticmethod
    @_run_client
    def tool_search_regulation(client: QdrantClient, query: str, limit: int = 2) -> list[dict]:

        query = f"query: {query}"
        vector = RegulationTools.MODEL.encode(query).tolist()

        results = client.query_points(
            collection_name=RegulationTools.COLLECTION,
            query=vector,
            limit=limit,
        ).points

        result = []
        for point in results:

            result.append({
                "score": round(point.score, 3),
                "text": point.payload.get("text")
            })
        print(result)
        return result

RegulationTools.rebuild_db()