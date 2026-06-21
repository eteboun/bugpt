import requests

from bs4 import BeautifulSoup, Tag
from typing import ClassVar
from utils import Cursor, to_text
from regulation_parser import RegulationParser

class ErasmusRegulations:

    URL: ClassVar[str] = "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662/"
    REGULATION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"

    @classmethod
    def _is_empty(cls, tag: Tag) -> bool:
        if tag is not None:

            is_empty = not tag.get_text(strip=True) and not tag.find()

            if is_empty:
                return True

        return False

    @classmethod
    def _get_soup(cls) -> BeautifulSoup:

        response = requests.get(cls.URL, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @classmethod
    def _get_regulations_container(cls):

        soup = cls._get_soup()
        regulations_container = soup.select_one(cls.REGULATION_SELECTOR)

        if regulations_container is not None:
            return regulations_container
        else:
            raise ValueError("No regulations found")

    @classmethod
    def _get_chunks(cls) -> list[dict]:

        regulations_container = cls._get_regulations_container()
        documentary = [element
                       for element in regulations_container.select("p, ol")
                       if not cls._is_empty(element)]

        cursor = Cursor(documentary)
        parser = RegulationParser(cursor)

        chunks = parser.run()

        return chunks




print(to_text(ErasmusRegulations._get_chunks()))