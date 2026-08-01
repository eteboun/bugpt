import requests
import os

from pathlib import Path
from dataclasses import dataclass

from regulation_rag.chunker.models import Chunk
from regulation_rag.chunker.config import ChunkerConfig
from regulation_rag.models import Document
from regulation_rag.html_parser.document_tree import HtmlDocumentTree
from regulation_rag.chunker.engine import Chunker
from regulation_rag.normalizers import *

@dataclass
class PipelineConfig:
    chunker: Chunker
    normalizer: type[HtmlNormalizer]
    url: str

class Pipeline:

    DOCUMENT_TYPE_MAPPING: ClassVar[dict[str, PipelineConfig]] = {
        "dormitory": PipelineConfig(
            chunker=Chunker(ChunkerConfig("dormitory")),
            normalizer=DormitoryNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
        ),
        "erasmus": PipelineConfig(
            chunker=Chunker(ChunkerConfig("erasmus")),
            normalizer=ErasmusNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662",
        ),
        "undergraduate": PipelineConfig(
            chunker=Chunker(ChunkerConfig("undergraduate")),
            normalizer=UndergraduateNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-lisans-egitim-ve-ogreti/657",
        ),
        "graduate": PipelineConfig(
            chunker=Chunker(ChunkerConfig("graduate")),
            normalizer=GraduateNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-lisansustu-egitim-ve-og/656",
        ),
        "major": PipelineConfig(
            chunker=Chunker(ChunkerConfig("major")),
            normalizer=MajorNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661",
        ),
        "minor": PipelineConfig(
            chunker=Chunker(ChunkerConfig("minor")),
            normalizer=MinorNormalizer,
            url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-yan-dal-programlari-yon/668",
        ),
    }

    CONTENT_SELECTOR: ClassVar[str] = "div.inner-page__content"
    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"

    def __init__(self,
                 document_type: str,
                 collection_name: str,
                 use_cache: bool = True
                 ) -> None:

        pipe_info = self.DOCUMENT_TYPE_MAPPING.get(document_type)
        if not pipe_info:
            raise Exception(f"Unknown pipeline: {document_type}")

        cached_dir = Path(__file__).resolve().parent / "normalized_htmls" / f"{document_type}.txt"
        if use_cache:

            if os.path.exists(cached_dir):
                normalized_html_text = cached_dir.read_text(encoding="utf-8")
            else:
                raise Exception(f"Cache does not exist: {document_type}")

        else:

            response = requests.get(pipe_info.url, timeout=10)
            response.raise_for_status()

            html_text = response.text
            temp_soup = BeautifulSoup(html_text, "html.parser")

            normalized_soup = self._normalize_soup(pipe_info.normalizer, temp_soup)
            normalized_content_container = self._get_content_container(normalized_soup)

            normalized_html_text = str(normalized_content_container)
            with open(cached_dir, "w", encoding="utf-8") as f:
                f.write(normalized_html_text)

        self.soup = BeautifulSoup(normalized_html_text, "html.parser")
        self.document_type = document_type
        self.collection_name = collection_name

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
            raise ValueError("No regulation_rag found")

        return soup

    def _get_document_tree(self) -> Document:
        content_container = self._get_content_container(self.soup)
        parser = HtmlDocumentTree(content_container)

        document = parser.run()
        document.document_type = self.document_type

        return document

    def _get_chunks(self) -> list[Chunk]:

        chunker = (self.DOCUMENT_TYPE_MAPPING
                   .get(self.document_type)
                   .chunker)

        document = self._get_document_tree()
        chunks = chunker.run(document)

        return chunks

    def run(self) -> list[Chunk]:
        return self._get_chunks()