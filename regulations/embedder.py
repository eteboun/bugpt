import requests

from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
from typing import ClassVar
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from regulations.parser import Parser

class Embedder:

    URL: ClassVar[str]
    PARSER: ClassVar[type[Parser]]
    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"
    COLLECTION_NAME: ClassVar[str] = "regulations"

    @classmethod
    def _get_soup(cls) -> BeautifulSoup:

        response = requests.get(cls.URL, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @classmethod
    def _get_regulations_container(cls) -> BeautifulSoup:

        soup = cls._get_soup()
        content_container = soup.select_one(cls.CONTENT_SELECTOR)

        if content_container is not None:
            return content_container
        else:
            raise ValueError("No regulations found")

    @classmethod
    def _get_chunks(cls) -> list[dict]:

        regulations_container = cls._get_regulations_container()
        parser = cls.PARSER(regulations_container)

        chunks = parser.run()

        return chunks

    @classmethod
    def _embed_chunks(cls, chunks: list[dict], model: SentenceTransformer) -> list[dict]:

        passages = [
            "passage: " + chunk["embedding_text"]
            for chunk in chunks
        ]

        embeddings = model.encode(
            passages,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding.tolist()

        return chunks

    @classmethod
    def _save_chunks(cls, chunks: list[dict], client: QdrantClient) -> None:

        if not chunks:
            return

        if not client.collection_exists(cls.COLLECTION_NAME):

            client.create_collection(
                collection_name=cls.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=len(chunks[0]["embedding"]),
                    distance=Distance.COSINE
                )
            )

        points = [
            PointStruct(
                id=chunk["point_id"],
                vector=chunk["embedding"],
                payload=chunk["payload"]
            ) for chunk in chunks
        ]

        client.upsert(
            collection_name=cls.COLLECTION_NAME,
            points=points
        )

    @classmethod
    def run(cls, client: QdrantClient, model: SentenceTransformer) -> None:
        chunks = cls._get_chunks()
        embedded_chunks = cls._embed_chunks(chunks, model)
        cls._save_chunks(embedded_chunks, client)
