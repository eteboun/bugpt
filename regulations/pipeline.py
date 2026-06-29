import json
import requests

from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup, Tag
from typing import ClassVar
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from regulations.chunking.chunk_structure import Chunk
from regulations.chunking.chunker_config import ChunkerConfig
from regulations.html_document_tree import HtmlDocumentTree
from regulations.normalizer import Normalizer
from regulations.chunking.chunker import Chunker

class Pipeline:

    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    def __init__(self, url: str,
                 collection_name: str,
                 normalizer: type[Normalizer],
                 chunker_config_name: str):

        with open(f"../configs/{chunker_config_name}.json", "r") as f:
            options = json.load(f)

        self.url = url
        self.collection_name = collection_name
        self.normalizer = normalizer

        chunker_config = ChunkerConfig()
        chunker_config.add_options(options)
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

    def _get_chunks(self) -> list[Chunk]:

        tree = self._get_html_tree()
        chunks = self.chunker.run(tree)

        return chunks

    def _save_chunks(self, model: SentenceTransformer, client: QdrantClient) -> None:

        chunks = self._get_chunks()

        if not client.collection_exists(self.collection_name):

            client.create_collection(
                collection_name=self.collection_name,
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
            collection_name=self.collection_name,
            points=points
        )

    def run(self, model: SentenceTransformer, client: QdrantClient) -> None:
        self._save_chunks(model=model, client=client)