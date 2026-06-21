from bs4 import Tag, NavigableString
from utils import Cursor
from typing import ClassVar

import re

class Parser:

    CHUNK_TYPES: ClassVar[set] = {
        "instruction",
        "definition"
    }

    def __init__(self, cursor: Cursor):
        self.cursor = cursor

    @staticmethod
    def _tag_to_text(tag: Tag) -> str:
        return tag.get_text(" ", strip=True)

    def _is_ending(self, ending: Tag) -> bool:

        if ending is None:
            return False

        text = self._tag_to_text(ending)
        number_match = re.match(r"^\s*\(\d+\)\s*", text)
        letter_match = re.match(r"^\s*\([a-z]+\)\s*", text)

        if ending.find() is None and len(text) > 0:
            return not bool(number_match) and not bool(letter_match)

        return False

    def _is_article(self, article: Tag | None) -> bool:

        if article is None:
            return False

        has_header = False
        has_string = False
        for child in article.contents:

            if isinstance(child, NavigableString) and len(child.strip()) > 0:
                has_string = True

            if isinstance(child, Tag) and child.name == "strong" and len(self._tag_to_text(child)) > 0:
                has_header = True

        return has_string and has_header

    def _is_paragraph(self, article: Tag) -> bool:

        if article is None:
            return False

        text = self._tag_to_text(article)
        match = re.match(r"^\s*\(\d+\)\s*", text)

        if article.find() is None and len(text) > 0:
            return bool(match)

        return False

    def _is_item(self, item: Tag) -> bool:

        if item is None:
            return False

        text = self._tag_to_text(item)
        match = re.match(r"^\s*\([a-z]+\)\s*", text)

        if item.find() is None and len(text) > 0:

            return bool(match)

        return False

    def _is_title(self, title: Tag | None) -> bool:

        if title is None:
            return False

        has_header = False
        for child in title.contents:

            if isinstance(child, Tag) and child.name == "strong" and len(self._tag_to_text(child)) > 0:
                has_header = True

        if not has_header:
            return False

        article = self.cursor.peek(n=2)

        if self._is_article(article):
            return True

        return False

    def _parse_chapters(self) -> list[dict]:

        chapters = []

        chapter_number = self._tag_to_text(self.cursor.next())
        chapter_name = self._tag_to_text(self.cursor.next())
        titles = self._parse_titles()

        for title in titles:
            title["metadata"]["chapter_number"] = chapter_number
            title["metadata"]["chapter_name"] = chapter_name
            chapters.append(title)

        while self.cursor.peek() is not None:
            chapter_number = self._tag_to_text(self.cursor.next())
            chapter_name = self._tag_to_text(self.cursor.next())
            titles = self._parse_titles()

            for title in titles:
                title["metadata"]["chapter_number"] = chapter_number
                title["metadata"]["chapter_name"] = chapter_name
                chapters.append(title)

        return chapters

    def _parse_titles(self) -> list[dict]:

        titles = []

        title = self._tag_to_text(self.cursor.next())
        articles = self._parse_articles()

        for article in articles:
            article["metadata"]["article_title"] = title
            titles.append(article)

        while self._is_title(self.cursor.peek()):

            title = self._tag_to_text(self.cursor.next())
            articles = self._parse_articles()

            for article in articles:
                article["metadata"]["article_title"] = title
                titles.append(article)

        return titles

    def _parse_articles(self) -> list[dict]:

        articles = self._parse_article()

        while self._is_article(self.cursor.peek()):
            articles.extend(self._parse_article())

        return articles

    def _parse_article(self) -> list[dict]:

        article = self.cursor.peek()
        article_number = self._get_article_number(article)

        paragraphs = self._parse_paragraph(article_number)

        while self._is_paragraph(self.cursor.peek()):
            paragraphs.extend(self._parse_paragraph(article_number))

        for paragraph in paragraphs:
            paragraph["metadata"]["article_number"] = article_number

        return paragraphs

    def _parse_paragraph(self, article_number) -> list[dict]:

        paragraph = self.cursor.next()
        paragraph_content = self._get_paragraph_string(paragraph)
        paragraph_number = self._get_paragraph_number(paragraph)

        if (next_tag := self.cursor.peek()) is not None and next_tag.name == "ol":

            starting = TextCleaner.remove_colon(paragraph_content)

            ol = self.cursor.next()
            ol_elements = TextCleaner.remove_comma(self._get_ordered_list_elements(ol))

            if self._is_ending(self.cursor.peek()):

                ending_tag = self.cursor.next()
                ending = self._get_paragraph_string(ending_tag)

                paragraphs = [{
                                "metadata": {
                                    "chunk_type": "instruction",
                                    "paragraph_number": paragraph_number,
                                },

                                "text": f"{starting} {element} {ending}",
                                  } for element in ol_elements]

            else:

                paragraphs = [{
                                "metadata": {
                                    "chunk_type": "instruction",
                                    "paragraph_number": paragraph_number,
                                },

                                "text": f"{starting} {element}",
                                  } for element in ol_elements]

        else:

                paragraphs = [{
                    "metadata": {
                        "chunk_type": "instruction",
                        "paragraph_number": paragraph_number,
                    },

                    "text": paragraph_content,
                }]

        items = self._parse_items()
        if len(items) > 0:

            paragraphs = [{
                "text": f"{paragraph["text"]} {item["item_content"]}",
                "metadata": {
                    "paragraph_number": paragraph_number,
                    "chunk_type": "instruction",
                    "item_letter": item["item_letter"],
                }
            } for paragraph in paragraphs
                for item in items]

        return paragraphs

    def _parse_items(self) -> list[dict]:

        items = []

        while self._is_item(self.cursor.peek()):
            item = self.cursor.next()
            item_letter = self._get_item_letter(item)
            item_content = self._get_item_string(item)

            items.append({
                "item_letter": item_letter,
                "item_content": item_content,
            })

        return items

    def _get_ordered_list_elements(self, ol: Tag) -> list[str]:
        return [
            self._tag_to_text(li)
            for li in ol.find_all("li")
        ]

    def _get_paragraph_string(self, paragraph: Tag) -> str:
        strings = [
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ]
        text = " ".join(strings)

        cleaned_text = re.sub(r"^\s*\(\d+\)\s*", "", text)
        return cleaned_text

    def _get_article_number(self, article: Tag) -> int:
        header = article.select_one("strong")
        text = self._tag_to_text(header)

        match = re.search(r"\d+", text)

        if match is None:
            raise ValueError("Could not extract article number")

        return int(match.group())

    def _get_paragraph_number(self, paragraph: Tag) -> int:
        strings = [
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ]
        text = " ".join(strings)
        match = re.match(r"^\s*\((\d+)\)\s*", text)

        if match is None:
            raise ValueError("Could not extract paragraph number")

        return int(match.group(1))

    def _get_item_letter(self, item: Tag) -> str:

        text = self._tag_to_text(item)
        match = re.match(r"^\(([a-z]+)\)", text)

        if match is None:
            raise ValueError("Could not extract paragraph number")

        return match.group(1)

    def _get_item_string(self, item: Tag) -> str:

        text = self._tag_to_text(item)

        cleaned_text = re.sub(r"^\s*\([a-z]+\)\s*", "", text)
        return cleaned_text

    def run(self):
        return self._parse_chapters()


class TextCleaner:

    @classmethod
    def remove_colon(cls, element: str) -> str:
        return (element
                .strip()
                .removesuffix(":")
                )

    @classmethod
    def remove_comma(cls, elements: list[str]) -> list[str]:
        return [element
                .strip()
                .removesuffix(",")
                for element in elements]

    @classmethod
    def add_period(cls, element: str) -> str:
        return (element
                .strip()
                .removesuffix(".") + ".")