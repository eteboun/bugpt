from typing import ClassVar
from bs4 import Tag, NavigableString
import re

class ComponentOperations:

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
        return tag is not None and bool(ComponentOperations.tag_to_text(tag))

    @staticmethod
    def has_strong(tag: Tag | None) -> bool:
        if tag is None:
            return False

        for header in tag.select("strong"):
            if ComponentOperations.tag_to_text(header):
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

        return ComponentOperations.has_string(tag) and ComponentOperations.has_strong(tag)

    @staticmethod
    def is_title(tag: Tag) -> bool:

        if tag is None:
            return False

        return not ComponentOperations.has_string(tag) and ComponentOperations.has_strong(tag)

    @staticmethod
    def is_plain_text(tag: Tag) -> bool:

        if tag is None:
            return False

        return ComponentOperations.has_string(tag) and not ComponentOperations.has_strong(tag)

    @staticmethod
    def is_paragraph(paragraph: Tag) -> bool:

        is_valid = ComponentOperations.is_plain_text(paragraph)
        if not is_valid:
            return False

        text = ComponentOperations.tag_to_text(paragraph)
        match = ComponentOperations.PARAGRAPH_PATTERN.match(text)

        return bool(match)

    @staticmethod
    def is_item(item: Tag) -> bool:

        is_valid = ComponentOperations.is_plain_text(item)
        if not is_valid:
            return False

        text = ComponentOperations.tag_to_text(item)
        match = ComponentOperations.ITEM_PATTERN.match(text)

        return bool(match)

    @staticmethod
    def is_sub_item_or_ending(element: Tag) -> bool:
        is_valid = ComponentOperations.is_plain_text(element)
        if not is_valid:
            return False

        text = ComponentOperations.tag_to_text(element)
        item_match = ComponentOperations.ITEM_PATTERN.match(text)
        paragraph_match = ComponentOperations.PARAGRAPH_PATTERN.match(text)

        return not bool(item_match) and not bool(paragraph_match)

    @staticmethod
    def get_paragraph_string(paragraph: Tag) -> str:

        text = " ".join([
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ])

        cleaned_text = ComponentOperations.PARAGRAPH_PATTERN.sub("", text)
        return cleaned_text

    @staticmethod
    def get_article_number(article: Tag) -> int:

        text = " ".join(ComponentOperations.tag_to_text(element)
                        for element in article.select("strong"))

        match = re.search(r"\d+", text)

        if match is None:
            raise ValueError("Could not extract article number")

        return int(match.group())

    @staticmethod
    def get_paragraph_number(paragraph: Tag) -> int:

        text = " ".join([
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ])
        match = ComponentOperations.PARAGRAPH_PATTERN.match(text)

        if match is None:
            raise ValueError("Could not extract paragraph number")

        return int(match.group(1))

    @staticmethod
    def get_item_letter(item: Tag) -> str:

        text = ComponentOperations.tag_to_text(item)

        match = ComponentOperations.ITEM_PATTERN.match(text)

        if match is None:
            raise ValueError("Could not extract item letter")

        return match.group(1)

    @staticmethod
    def get_item_string(item: Tag) -> str:

        text = ComponentOperations.tag_to_text(item)

        cleaned_text = ComponentOperations.ITEM_PATTERN.sub("", text)
        return cleaned_text

class TextCleaner:

    @staticmethod
    def remove_colon(element: str) -> str:
        return (element
                .strip()
                .removesuffix(":")
                )

    @staticmethod
    def remove_comma(elements: list[str]) -> list[str]:
        return [element
                .strip()
                .removesuffix(",")
                for element in elements]

    @staticmethod
    def add_period(element: str) -> str:
        return (element
                .strip()
                .removesuffix(".") + ".")

    @staticmethod
    def remove_hyphen(element: str) -> str:
        return (re.sub(r"^\s*[-–]+\s*|\s*[-–]+\s*$", "", element)
                .strip())

