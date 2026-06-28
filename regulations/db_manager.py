from functools import wraps
from typing import ClassVar
from pathlib import Path
import shutil

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from double_major_regulations.regulation_pipeline import DoubleMajorRegulationEmbedder
from erasmus_regulations.regulation_pipeline import ErasmusRegulationEmbedder

class DBManager:

    MODEL: ClassVar[SentenceTransformer] = SentenceTransformer("intfloat/multilingual-e5-base")

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
    def build_db(self, client):

        DoubleMajorRegulationEmbedder.run(client, self.MODEL)
        ErasmusRegulationEmbedder.run(client, self.MODEL)

    def delete_db(self):
        path = Path(self.path)
        if path.exists():
            shutil.rmtree(path)
        else:
            raise Exception("Path doesn't exist")

    @_run_client
    def search_db(self, client, query: str, collection_name: str, limit: int = 5):

        query = f"query: {query}"
        vector = self.MODEL.encode(query).tolist()

        results = client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
        ).points

        for point in results:
            print(f"score: {point.score}")
            print(f"text: {point.payload["text"]}")

manager = DBManager("./storage")
manager.search_db(
    query="çift anadal programına başvurma şartları nelerdir?",
    collection_name="regulations"
)
