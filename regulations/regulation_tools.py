from functools import wraps
from typing import ClassVar
from pathlib import Path
import shutil

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from regulations.pipelines import (dormitory_pipeline,
                                   erasmus_pipeline,
                                   major_pipeline)

class RegulationTools:

    MODEL: ClassVar[SentenceTransformer] = SentenceTransformer("intfloat/multilingual-e5-base")
    COLLECTION: ClassVar[str] = "regulations"

    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def _run_client(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            client = QdrantClient(path=self.path)
            try:
                return func(self, client, *args, **kwargs)
            finally:
                client.close()

        return wrapper

    @_run_client
    def build_db(self, client: QdrantClient):

        dormitory_pipeline.run_pipeline(model=self.MODEL, client=client)
        erasmus_pipeline.run_pipeline(model=self.MODEL, client=client)
        major_pipeline.run_pipeline(model=self.MODEL, client=client)

    def rebuild_db(self):
        self.delete_db()
        self.build_db()

    def delete_db(self):
        path = Path(self.path)
        if path.exists():
            shutil.rmtree(path)
        else:
            raise Exception("Path doesn't exist")

    @_run_client
    def tool_search_regulation(self, client, query: str, limit: int = 5):

        query = f"query: {query}"
        vector = self.MODEL.encode(query).tolist()

        results = client.query_points(
            collection_name=self.COLLECTION,
            query=vector,
            limit=limit,
        ).points
