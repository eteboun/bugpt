from bs4 import Tag, NavigableString
from typing import ClassVar, override
from regulations.parser import Parser, TextCleaner

import re

class RegulationParser(Parser):

    NON_BOLD_TITLES: ClassVar[set] = {"Değerlendirme ve Yerleştirme",
                                      "Yürürlük",
                                      "Yürütme"}

    CHUNK_TYPES = {
        "instruction",
        "definition",
    }

    ITEM_PATTERN = re.compile(r"^\s*\(([a-zçğıöşü]+)\)\s*")
    PARAGRAPH_PATTERN = re.compile(r"^\s*\((\d+)\)\s*")

    def __init__(self, content_container: Tag):
        super().__init__(content_container)
        self.special_articles = {
            4: self.article_4,
            5: self.article_5,
            9: self.article_9,
            13: self.article_13,
            26: self.article_26,
        }

    def article_4(self, **kwargs) -> list[dict]:

        paragraph_number = kwargs["paragraph_number"]

        paragraphs = []

        ol = self.cursor.next()
        ol_elements = TextCleaner.remove_comma(self._get_ordered_list_elements(ol))

        ending_tag = self.cursor.next()
        ending = self._get_ending_string(ending_tag)

        for element in ol_elements:
            colon = element.find(":")

            term = element[:colon].strip()

            definition_base = element[colon + 1:].strip()
            definition = f"{definition_base} {ending}"

            paragraphs.append({
                "payload": {
                    "chunk_type": "definition",
                    "paragraph_number": paragraph_number,
                    "term": term,
                    "text": f"{term} şu anlama gelir: {definition}",
                },
            })

        return paragraphs

    def article_5(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        colon = paragraph_content.find(":")

        term = paragraph_content[:colon].strip()
        term = self.PARAGRAPH_PATTERN.sub("", term)
        definition = paragraph_content[colon + 1:].strip()

        return [{
            "payload": {
                "text": f"{term} şu anlama gelir: {definition}",
                "chunk_type": "definition",
                "paragraph_number": paragraph_number,
                "term": term,
            },
        }]

    def article_9(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        starting = TextCleaner.remove_colon(paragraph_content)

        ol_1 = self.cursor.next()
        ol_1_elements = self._get_ordered_list_elements(ol_1)

        ol_1_last_item_ending = self._get_ending_string(self.cursor.next())
        ol_1_elements[-1] = f"{ol_1_elements[-1]} {ol_1_last_item_ending}"

        ol_2 = self.cursor.next()
        ol_2_elements = self._get_ordered_list_elements(ol_2)

        ol_elements = TextCleaner.remove_comma(ol_1_elements + ol_2_elements)

        ending_tag = self.cursor.next()
        ending = self._get_ending_string(ending_tag)

        return [{
                              "payload": {
                                  "chunk_type": "instruction",
                                  "paragraph_number": paragraph_number,
                                  "text": f"{starting} {element} {ending}",
                              },
                          } for element in ol_elements]


    def article_13(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        starting = TextCleaner.remove_colon(paragraph_content)

        ol = self.cursor.next()
        ol_elements = TextCleaner.remove_comma(self._get_ordered_list_elements(ol))

        ending_tag = self.cursor.next()
        ending = (self
                  ._get_ending_string(ending_tag)
                  .replace("Yukarıdaki koşulları", "Bu koşulu"))

        return [{
                              "payload": {
                                  "chunk_type": "instruction",
                                  "paragraph_number": paragraph_number,
                                  "text": f"{starting} {element} {ending}",
                              },
                          } for element in ol_elements]

    def article_26(self, **kwargs) -> list[dict]:

        paragraph_content = kwargs["paragraph_content"]
        paragraph_number = kwargs["paragraph_number"]

        paragraph_content = TextCleaner.add_period(paragraph_content)

        return [({
            "payload": {
                "chunk_type": "instruction",
                "paragraph_number": paragraph_number,
                "text": paragraph_content,
            },
        })
]
    @override
    @classmethod
    def _is_paragraph(cls, article: Tag) -> bool:

        if article is None:
            return False

        text = TextCleaner.remove_hyphen(cls._tag_to_text(article))
        match = cls.PARAGRAPH_PATTERN.match(text)

        if article.find() is None and len(text) > 0:

            if text in cls.NON_BOLD_TITLES:
                return False

            return bool(match)

        return False

    @override
    @classmethod
    def _is_item(cls, item: Tag) -> bool:

        if item is None:
            return False

        text = TextCleaner.remove_hyphen(cls._tag_to_text(item))
        match = cls.ITEM_PATTERN.match(text)

        if item.find() is None and len(text) > 0:

            if text in cls.NON_BOLD_TITLES:
                return False

            return bool(match)

        return False

    @override
    @classmethod
    def _is_title(cls, title: Tag | None) -> bool:

        if title is None:
            return False

        has_header = False
        non_bold = False
        no_string = True
        for child in title.contents:

            if isinstance(child, Tag) and child.name == "strong" and len(cls._tag_to_text(child)) > 0:
                has_header = True

            if isinstance(child, NavigableString) and len(child.strip()) > 0:
                no_string = False

            if isinstance(child, NavigableString) and child.strip() in cls.NON_BOLD_TITLES:
                non_bold = True

        if non_bold:
            return True

        return has_header and no_string

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