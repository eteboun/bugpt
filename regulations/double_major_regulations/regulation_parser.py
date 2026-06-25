from typing import ClassVar, override
from bs4 import Tag, NavigableString
from regulations.parser import Parser

import re

class RegulationParser(Parser):

    ITEM_PATTERN = re.compile(r"^\s*\(?([a-zçğıöşü]+)\)\s*")
    PARAGRAPH_PATTERN = re.compile(r"^\s*\((\d+)\)\s*")

    INCOMPATIBLE_TITLES: ClassVar[set] = {"Dayanak",
                                          "Çift ana dal Programında Başarı Şartı, Ders Yükü ve Süre",
                                          "Başvuru Süreci ve Kabul",
                                          "Çift ana dal Programından Ayrılma ve Çıkarılma"}

    def __init__(self, content_container: Tag):
        super().__init__(content_container)

    @override
    def _parse_titles(self) -> list[dict]:

        titles = self._parse_title()

        while (((next_tag := self.cursor.peek()) is not None
               and (bold := next_tag.find("strong")) is not None
               and self._tag_to_text(bold) in self.INCOMPATIBLE_TITLES)
               or (self._is_title(self.cursor.peek())
                   and self._is_article(self.cursor.peek(n=2)))):

            titles.extend(self._parse_title())

        return titles

    @override
    def _parse_title(self) -> list[dict]:
        titles = []

        if ((next_tag := self.cursor.peek()) is not None
                and (bold := next_tag.find("strong")) is not None
                and self._tag_to_text(bold) in self.INCOMPATIBLE_TITLES):

            container = self.cursor.next()
            title_tag = container.find("strong")
            article_element = title_tag.find_next_sibling("strong")\
                if self._tag_to_text(bold) != "Çift ana dal Programından Ayrılma ve Çıkarılma"\
                else self._tag_to_text(title_tag.find_next_sibling("strong"))
            paragraph_text = " ".join([
                str_.strip() for str_ in container.contents if isinstance(str_, NavigableString)
            ])

            title = self._tag_to_text(title_tag)
            article_number = self._get_article_number(article_element)
            paragraph_number = self._get_paragraph_number(paragraph_text)
            paragraph_content = self._get_paragraph_string(paragraph_text)

            chunk = {
                "payload": {
                    "chunk_type": "instruction",
                    "paragraph_number": paragraph_number,
                    "article_title": title,
                    "article_number": article_number,
                    "text": paragraph_content,
                }
            }

            titles.append(chunk)

            while self._is_paragraph(self.cursor.peek()):
                paragraphs = self._parse_paragraph(article_number)

                for paragraph in paragraphs:
                    paragraph["payload"]["article_number"] = article_number
                    paragraph["payload"]["article_title"] = title

                    titles.append(paragraph)

        else:

            title = self._tag_to_text(self.cursor.next())
            articles = self._parse_articles()

            for article in articles:
                article["payload"]["article_title"] = title
                titles.append(article)

        return titles

    @override
    @classmethod
    def _is_article(cls, article: Tag | None) -> bool:

        if article is None:
            return False

        if (bold := article.find("strong")) is not None and cls._tag_to_text(bold) in cls.INCOMPATIBLE_TITLES:
            return False

        return super()._is_article(article)
