from typing import ClassVar, Literal
from bs4 import Tag, NavigableString
import re

class ParserFunctions:

    ITEM_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s*\(?([a-zçğıöşü]+)\)\s*")
    PARAGRAPH_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^\s*\(?(\d+)\)\s*")

    CHAPTER_NUMBER_MAPPING: ClassVar[dict[str, int]] = {
        "BİRİNCİ": 1,
        "İKİNCİ": 2,
        "ÜÇÜNCÜ": 3,
        "DÖRDÜNCÜ": 4,
        "BEŞİNCİ": 5,
        "ALTINCI": 6,
        "YEDİNCİ": 7,
        "SEKİZİNCİ": 8,
        "DOKUZUNCU": 9,
        "ONUNCU": 10,
        "ON BİRİNCİ": 11,
        "ON İKİNCİ": 12,
        "ON ÜÇÜNCÜ": 13,
        "ON DÖRDÜNCÜ": 14,
        "ON BEŞİNCİ": 15,
    }

    @staticmethod
    def tag_to_text(tag: Tag) -> str:
        return tag.get_text(" ", strip=True)

    @staticmethod
    def get_string(tag: Tag) -> str:
        strings = [
            child
            for child in tag.contents
            if isinstance(child, NavigableString) and child.strip()
        ]

        return " ".join(strings)

    @staticmethod
    def has_text(tag: Tag | None) -> bool:
        return tag is not None and bool(ParserFunctions.tag_to_text(tag))

    @staticmethod
    def has_strong(tag: Tag | None) -> bool:
        if tag is None:
            return False

        for header in tag.select("strong"):
            if ParserFunctions.tag_to_text(header):
                return True

        return False

    @staticmethod
    def has_string(tag: Tag | None) -> bool:
        if tag is None:
            return False

        for child in tag.contents:
            if isinstance(child, NavigableString) and child.strip():
                return True

        return False

    @staticmethod
    def is_article(tag: Tag) -> bool:

        if tag is None:
            return False

        return ParserFunctions.has_string(tag) and ParserFunctions.has_strong(tag)

    @staticmethod
    def is_title(tag: Tag) -> bool:

        if tag is None:
            return False

        return not ParserFunctions.has_string(tag) and ParserFunctions.has_strong(tag)

    @staticmethod
    def is_plain_text(tag: Tag) -> bool:

        if tag is None:
            return False

        return ParserFunctions.has_string(tag) and not ParserFunctions.has_strong(tag)

    @staticmethod
    def is_paragraph(tag: Tag) -> bool:

        is_valid = ParserFunctions.is_plain_text(tag)
        if not is_valid:
            return False

        text = ParserFunctions.tag_to_text(tag)
        match = ParserFunctions.PARAGRAPH_PATTERN.match(text)

        return bool(match)

    @staticmethod
    def is_item_list(tag: Tag) -> bool:

        if tag is None:
            return False

        return tag.name == "ol"

    @staticmethod
    def is_lettered_item(tag: Tag) -> bool:

        is_valid = ParserFunctions.is_plain_text(tag)
        if not is_valid:
            return False

        text = ParserFunctions.tag_to_text(tag)
        match = ParserFunctions.ITEM_PATTERN.match(text)

        return bool(match)

    @staticmethod
    def is_sub_item_or_ending(tag: Tag) -> bool:
        is_valid = ParserFunctions.is_plain_text(tag)
        if not is_valid:
            return False

        text = ParserFunctions.tag_to_text(tag)
        item_match = ParserFunctions.ITEM_PATTERN.match(text)
        paragraph_match = ParserFunctions.PARAGRAPH_PATTERN.match(text)

        return not bool(item_match) and not bool(paragraph_match)

    @staticmethod
    def get_item_list_strings(item_list: Tag) -> list[str]:

        return [ParserFunctions.tag_to_text(li)
                for li in item_list.find_all("li", recursive=False)]

    @staticmethod
    def get_paragraph_string(paragraph: Tag) -> str:

        text = " ".join([
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ])

        cleaned_text = ParserFunctions.PARAGRAPH_PATTERN.sub("", text)
        return cleaned_text

    @staticmethod
    def get_article_number(article: Tag) -> int:

        text = " ".join(ParserFunctions.tag_to_text(element)
                        for element in article.select("strong"))

        match = re.search(r"\d+", text)

        if match is None:
            raise ValueError("Could not extract article number")

        return int(match.group())

    @staticmethod
    def get_article_kind(article: Tag) -> Literal["temporary", "default"]:

        text = " ".join(ParserFunctions.tag_to_text(element)
                        for element in article.select("strong"))

        if "GEÇİCİ" in text:
            return "temporary"
        return "default"

    @staticmethod
    def get_paragraph_number(paragraph: Tag) -> int:

        text = " ".join([
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ])
        match = ParserFunctions.PARAGRAPH_PATTERN.match(text)

        if match is None:
            raise ValueError("Could not extract paragraph number")

        return int(match.group(1))

    @staticmethod
    def get_lettered_item_letter(item: Tag) -> str:

        text = ParserFunctions.tag_to_text(item)

        match = ParserFunctions.ITEM_PATTERN.match(text)

        if match is None:
            raise ValueError("Could not extract item letter")

        return match.group(1)

    @staticmethod
    def get_lettered_item_string(item: Tag) -> str:

        text = ParserFunctions.tag_to_text(item)

        cleaned_text = ParserFunctions.ITEM_PATTERN.sub("", text)
        return cleaned_text
