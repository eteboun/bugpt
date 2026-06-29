import requests

from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup, Tag
from typing import ClassVar
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from regulations.chunker_config import ChunkerConfig
from regulations.html_document_tree import HtmlDocumentTree
from regulations.normalizer import Normalizer
from regulations.chunker import Chunker

class Pipeline:

    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    def __init__(self, url: str,
                 collection_name: str,
                 normalizer: type[Normalizer],
                 chunker_config: ChunkerConfig):

        self.url = url
        self.collection_name = collection_name
        self.normalizer = normalizer
        self.chunker = Chunker(chunker_config)

        response = requests.get(self.url, timeout=10)
        response.raise_for_status()

        self.soup = BeautifulSoup(response.text, "html.parser")

    def _get_content_container(self) -> Tag:

        content_container = self.soup.select_one(self.CONTENT_SELECTOR, recursive=False)

        if content_container is not None:
            return content_container
        else:
            raise ValueError("No regulations found")

    def _normalize_content_container(self, content_container: Tag):
        regulation_container = content_container.select_one(self.DESCRIPTION_SELECTOR)
        self.normalizer.run(regulation_container, self.soup)

    def _get_html_tree(self) -> dict:

        content_container = self._get_content_container()
        self._normalize_content_container(content_container)

        parser = HtmlDocumentTree(content_container)

        tree = parser.run()

        return tree

    def _get_chunks(self) -> list[dict]:

        tree = self._get_html_tree()
        chunks = self.chunker.run(tree)

        return chunks

    @staticmethod
    def _embed_chunks(chunks: list[dict], model: SentenceTransformer) -> list[dict]:

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

    def _save_chunks(self, chunks: list[dict], client: QdrantClient) -> None:

        if not chunks:
            return

        if not client.collection_exists(self.collection_name):

            client.create_collection(
                collection_name=self.collection_name,
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
            collection_name=self.collection_name,
            points=points
        )