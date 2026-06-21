from bs4 import Tag, NavigableString
from utils import Cursor
from typing import ClassVar, override
from parser import Parser, TextCleaner

import re

class RegulationParser(Parser):

    NON_BOLD_TITLES: ClassVar[set] = {"Değerlendirme ve Yerleştirme",
                                      "Yürürlük",
                                      "Yürütme"}


    def __init__(self, cursor: Cursor):
        super().__init__(cursor)
        self.special_articles = {
            4: self.article_n4,
            5: self.article_n5,
            9: self.article_n9,
            13: self.article_n13,
            26: self.article_n26,
        }

    def article_n4(self, **kwargs) -> list[dict]:

        paragraph_number = kwargs["paragraph_number"]

        paragraphs = []

        ol = self.cursor.next()
        ol_elements = TextCleaner.remove_comma(self._get_ordered_list_elements(ol))

        ending_tag = self.cursor.next()
        ending = self._get_paragraph_string(ending_tag)

        for element in ol_elements:
            colon = element.find(":")

            term = element[:colon].strip()

            definition_base = element[colon + 1:].strip()
            definition = f"{definition_base} {ending}"

            paragraphs.append({
                "metadata": {
                    "chunk_type": "definition",
                    "paragraph_number": paragraph_number,
                    "term": term,
                },

                "text": f"{term} şu anlama gelir: {definition}",
            })

        return paragraphs

    def article_n5(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        colon = paragraph_content.find(":")

        term = paragraph_content[:colon].strip()
        term = re.sub(r"^\s*\(\d+\)\s*", "", term)
        definition = paragraph_content[colon + 1:].strip()

        return [{
            "metadata": {
                "chunk_type": "definition",
                "paragraph_number": paragraph_number,
                "term": term,
            },

            "text": f"{term} şu anlama gelir: {definition}",
        }]

    def article_n9(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        starting = TextCleaner.remove_colon(paragraph_content)

        ol_1 = self.cursor.next()
        ol_1_elements = self._get_ordered_list_elements(ol_1)

        ol_1_last_item_ending = self._tag_to_text(self.cursor.next())
        ol_1_elements[-1] = f"{ol_1_elements[-1]} {ol_1_last_item_ending}"

        ol_2 = self.cursor.next()
        ol_2_elements = self._get_ordered_list_elements(ol_2)

        ol_elements = TextCleaner.remove_comma(ol_1_elements + ol_2_elements)

        ending_tag = self.cursor.next()
        ending = self._get_paragraph_string(ending_tag)

        return [{
                              "metadata": {
                                  "chunk_type": "instruction",
                                  "paragraph_number": paragraph_number,
                              },

                              "text": f"{starting} {element} {ending}",
                          } for element in ol_elements]


    def article_n13(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        starting = TextCleaner.remove_colon(paragraph_content)

        ol = self.cursor.next()
        ol_elements = TextCleaner.remove_comma(self._get_ordered_list_elements(ol))

        ending_tag = self.cursor.next()
        ending = (self
                  ._get_paragraph_string(ending_tag)
                  .replace("Yukarıdaki koşulları", "Bu koşulu"))

        return [{
                              "metadata": {
                                  "chunk_type": "instruction",
                                  "paragraph_number": paragraph_number,
                              },

                              "text": f"{starting} {element} {ending}",
                          } for element in ol_elements]

    def article_n26(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        paragraph_content = TextCleaner.add_period(paragraph_content)

        return [({
            "metadata": {
                "chunk_type": "instruction",
                "paragraph_number": paragraph_number,
            },

            "text": paragraph_content,
        })
]
    @override
    def _is_paragraph(self, article: Tag) -> bool:

        if article is None:
            return False

        text = self._tag_to_text(article)
        match = re.match(r"^\s*\(\d+\)\s*", text)

        if article.find() is None and len(text) > 0:

            if text in self.NON_BOLD_TITLES:
                return False

            return bool(match)

        return False

    @override
    def _is_item(self, item: Tag) -> bool:

        if item is None:
            return False

        text = self._tag_to_text(item)
        match = re.match(r"^\s*\([a-z]+\)\s*", text)

        if item.find() is None and len(text) > 0:

            if text in self.NON_BOLD_TITLES:
                return False

            return bool(match)

        return False

    @override
    def _is_title(self, title: Tag | None) -> bool:

        if title is None:
            return False

        has_header = False
        non_bold = False
        for child in title.contents:

            if isinstance(child, Tag) and child.name == "strong" and len(self._tag_to_text(child)) > 0:
                has_header = True

            if isinstance(child, NavigableString) and child.strip() in self.NON_BOLD_TITLES:
                non_bold = True

        if not has_header and not non_bold:
            return False

        article = self.cursor.peek(n=2)

        if self._is_article(article):
            return True

        return False

    @override
    def _parse_paragraph(self, article_number) -> list[dict]:

        handler = self.special_articles.get(article_number)
        if handler is not None:

            paragraph = self.cursor.next()
            paragraph_content = self._get_paragraph_string(paragraph)
            paragraph_number = self._get_paragraph_number(paragraph)

            return handler(
                paragraph_content=paragraph_content,
                paragraph_number=paragraph_number
            )

        return super()._parse_paragraph(article_number)