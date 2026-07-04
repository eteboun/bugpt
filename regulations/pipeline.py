import requests

from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup, Tag
from typing import ClassVar
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from regulations.chunker.models import Chunk
from regulations.chunker.config import ChunkerConfig
from regulations.models import Document
from regulations.html_parser.document_tree import HtmlDocumentTree
from regulations.html_parser.normalizer import HtmlNormalizer
from regulations.chunker.engine import Chunker

class Pipeline:

    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    COLLECTION: ClassVar[str] = "regulations"

    def __init__(self, url: str,
                 normalizer: type[HtmlNormalizer],
                 chunker_config_name: str):

        chunker_config = ChunkerConfig(config_name=chunker_config_name)
        self.chunker = Chunker(chunker_config)

        self.url = url
        self.normalizer = normalizer

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

    def _get_document_tree(self) -> Document:

        content_container = self._get_content_container()
        self._normalize_content_container(content_container)

        parser = HtmlDocumentTree(content_container)

        document = parser.run()

        return document

    def _get_chunks(self) -> list[Chunk]:

        document = self._get_document_tree()
        chunks = self.chunker.run(document)

        return chunks

    def _save_chunks(self, model: SentenceTransformer, client: QdrantClient) -> None:

        chunks = self._get_chunks()

        if not client.collection_exists(self.COLLECTION):

            client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=VectorParams(
                    size=model.get_embedding_dimension(),
                    distance=Distance.COSINE
                )
            )

        points = [
            PointStruct(
                id=chunk.id,
                vector=model.encode(chunk.embedding_text).tolist(),
                payload=chunk.payload.as_dict()
            ) for chunk in chunks
        ]

        client.upsert(
            collection_name=self.COLLECTION,
            points=points
        )

    def run(self, model: SentenceTransformer, client: QdrantClient) -> None:
        self._save_chunks(model=model, client=client)