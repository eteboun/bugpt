import requests
import os

from pathlib import Path

from config.regulation_config import DOCUMENT_URL_MAPPING, REGULATION_DB_PATH, REGULATION_COLLECTION_NAME
from qdrant.client import run_client, add_to_collection

from models.regulation.chunk_models import Chunk
from preprocess.regulation.chunker.config import ChunkerConfig
from models.regulation.document_models import Document
from preprocess.regulation.html_parser.document_tree import HtmlDocumentTree
from preprocess.regulation.chunker.engine import Chunker
from preprocess.regulation.normalizers import *

class Pipeline:

    DOCUMENT_NORMALIZER_MAPPING: ClassVar[dict] = {
        "dormitory": DormitoryNormalizer,
        "erasmus": ErasmusNormalizer,
        "undergraduate": UndergraduateNormalizer,
        "graduate": GraduateNormalizer,
        "major": MajorNormalizer,
        "minor": MinorNormalizer,
    }

    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"
    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"

    def __init__(self,
                 document_type: str,
                 use_cache: bool = True
                 ) -> None:

        url = DOCUMENT_URL_MAPPING.get(document_type)
        if not url:
            raise Exception(f"Unknown pipeline: {document_type}")

        cached_dir = Path(__file__).resolve().parent / "normalized_htmls" / f"{document_type}.txt"
        if use_cache:

            if os.path.exists(cached_dir):
                normalized_html_text = cached_dir.read_text(encoding="utf-8")
            else:
                raise Exception(f"Cache does not exist: {document_type}")

        else:

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            html_text = response.text
            temp_soup = BeautifulSoup(html_text, "html.parser")

            normalizer = Pipeline.DOCUMENT_NORMALIZER_MAPPING.get(document_type)
            if not normalizer:
                raise Exception(f"Unknown normalizer: {document_type}")

            normalized_soup = self._normalize_soup(normalizer, temp_soup)
            normalized_content_container = self._get_content_container(normalized_soup)

            normalized_html_text = str(normalized_content_container)
            with open(cached_dir, "w", encoding="utf-8") as f:
                f.write(normalized_html_text)

        self.soup = BeautifulSoup(normalized_html_text, "html.parser")
        self.document_type = document_type
        self.chunker = Chunker(
            ChunkerConfig(self.document_type)
        )

    @staticmethod
    def _get_content_container(soup: BeautifulSoup) -> Tag:

        content_container = soup.select_one(Pipeline.CONTENT_SELECTOR, recursive=False)

        if content_container is not None:
            return content_container
        else:
            raise ValueError("No content found")

    @staticmethod
    def _normalize_soup(normalizer: type[HtmlNormalizer], soup: BeautifulSoup) -> BeautifulSoup:

        content_container = Pipeline._get_content_container(soup)
        regulation_container = content_container.select_one(Pipeline.DESCRIPTION_SELECTOR)

        if regulation_container is not None:
            normalizer.run(regulation_container, soup)
        else:
            raise ValueError("No regulation found")

        return soup

    def _get_document_tree(self) -> Document:
        content_container = self._get_content_container(self.soup)
        parser = HtmlDocumentTree(content_container)

        document = parser.run()
        document.document_type = self.document_type

        return document

    def _get_chunks(self) -> list[Chunk]:

        document = self._get_document_tree()
        chunks = self.chunker.run(document)

        return chunks

    @staticmethod
    def _save_chunks(chunks: list[Chunk]) -> None:
        chunks = [
            chunk.serialize() for chunk in chunks
        ]
        with run_client(db_path=REGULATION_DB_PATH) as client:
            add_to_collection(client=client, collection_name=REGULATION_COLLECTION_NAME, chunks=chunks)

    def run(self) -> None:
        chunks = self._get_chunks()
        self._save_chunks(chunks=chunks)