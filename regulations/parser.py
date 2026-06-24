from bs4 import Tag, NavigableString
from utils import Cursor
from typing import ClassVar
from uuid import uuid4

import re

class Parser:

    TR_MAP: ClassVar[dict] = str.maketrans({
        "ç": "c", "Ç": "C",
        "ğ": "g", "Ğ": "G",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ş": "s", "Ş": "S",
        "ü": "u", "Ü": "U",
    })

    CHUNK_TYPES: ClassVar[set[str]] = {
        "instruction",
        "definition"
    }

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

    def __init__(self, content_container: Tag):

        self.content_container = content_container

        base_class = content_container.get("class", [None])[0]
        if base_class is not None:
            target_class = f"{base_class}-description"
            regulation_container = content_container.find(
                "div",
                class_=target_class,
                recursive=False
            )
        else:
            raise ValueError("No regulations found")

        documentary = [element
                       for element in regulation_container.select("p, ol")
                       if not self._is_empty(element)]

        cursor = Cursor(documentary)
        self.cursor = cursor

    @classmethod
    def _is_empty(cls, tag: Tag) -> bool:
        if tag is not None:

            is_empty = not tag.get_text(strip=True) and not tag.find()

            if is_empty:
                return True

        return False

    @classmethod
    def _tag_to_text(cls, tag: Tag) -> str:
        return tag.get_text(" ", strip=True)

    @classmethod
    def _is_ending(cls, ending: Tag) -> bool:

        if ending is None:
            return False

        text = cls._tag_to_text(ending)
        number_match = re.match(r"^\s*\(\d+\)\s*", text)
        letter_match = re.match(r"^\s*\([a-z]+\)\s*", text)

        if ending.find() is None and len(text) > 0:
            return not bool(number_match) and not bool(letter_match)

        return False

    @classmethod
    def _is_article(cls, article: Tag | None) -> bool:

        if article is None:
            return False

        has_header = False
        has_string = False
        for child in article.contents:

            if isinstance(child, NavigableString) and len(child.strip()) > 0:
                has_string = True

            if isinstance(child, Tag) and child.name == "strong" and len(cls._tag_to_text(child)) > 0:
                has_header = True

        return has_string and has_header

    @classmethod
    def _is_paragraph(cls, article: Tag) -> bool:

        if article is None:
            return False

        text = cls._tag_to_text(article)
        match = re.match(r"^\s*\(\d+\)\s*", text)

        if article.find() is None and len(text) > 0:
            return bool(match)

        return False

    @classmethod
    def _is_item(cls, item: Tag) -> bool:

        if item is None:
            return False

        text = cls._tag_to_text(item)
        match = re.match(r"^\s*\([a-z]+\)\s*", text)

        if item.find() is None and len(text) > 0:

            return bool(match)

        return False

    @classmethod
    def _is_title(cls, title: Tag | None) -> bool:

        if title is None:
            return False

        has_header = False
        no_string = True
        for child in title.contents:

            if isinstance(child, Tag) and child.name == "strong" and len(cls._tag_to_text(child)) > 0:
                has_header = True

            if isinstance(child, NavigableString) and len(child.strip()) > 0:
                no_string = False

        return has_header and no_string

    def _add_main_title(self, chunks: list[dict]) -> None:

        base_class = self.content_container.get("class", [None])[0]
        if base_class is not None:
            target_class = f"{base_class}-header"
            title_selector = self.content_container.find(
                "div",
                class_=target_class,
                recursive=False
            )
        else:
            raise ValueError("No title found")

        main_title = self._tag_to_text(
            title_selector.select_one("h2")
        )

        for chunk in chunks:
            payload = chunk["payload"]
            payload["main_title"] = main_title

    @classmethod
    def _add_id(cls, chunks: list[dict]) -> None:

        for chunk in chunks:

            payload = chunk["payload"]

            base_slug = (chunk["payload"]["main_title"]
                         .translate(cls.TR_MAP)
                         .lower()
                         .replace(" ", "_"))
            base_slug = re.sub(r"[^a-z0-9]+", "_", base_slug).strip("_")

            chapter_id = f"chapter_{payload["chapter_number"]:02d}"
            article_id = f"article_{payload["article_number"]:02d}"
            paragraph_id = f"paragraph_{payload["paragraph_number"]:02d}"

            id_items = [base_slug, chapter_id, article_id, paragraph_id]

            if "item_letter" in payload:
                item_id = f"item_{payload["item_letter"]}"
                id_items.append(item_id)

            id_ = ":".join(id_items)

            chunk["payload"]["chunk_id"] = id_
            chunk["point_id"] = str(uuid4())

    @classmethod
    def _add_embedding_text(cls, chunks: list[dict]) -> None:

        for chunk in chunks:
            payload = chunk["payload"]
            text = chunk["payload"]["text"]

            parts = [
                f'Belge: {payload["main_title"]}',
                f'Bölüm: {payload["chapter_name"]}',
                f'Madde {payload["article_number"]}: {payload["article_title"]}',
            ]

            if "item_letter" in payload:
                parts.append(f'Paragraf {payload["paragraph_number"]}')
                parts.append(f'Bent {payload["item_letter"]}: {text}')
            else:
                parts.append(f'Paragraf {payload["paragraph_number"]}: {text}')

            embedding_text = "\n".join(parts)

            chunk["embedding_text"] = embedding_text

    def _parse_chapters(self) -> list[dict]:

        chapters = []

        chapter_label = self._tag_to_text(self.cursor.next())

        chapter_number_str = (re.sub(r"\s+BÖLÜM\s*$", "", chapter_label)
                              .strip()
                              .upper())
        chapter_number = self.CHAPTER_NUMBER_MAPPING.get(chapter_number_str)

        if chapter_number is None:
            raise ValueError(f"Unknown chapter label: {chapter_label!r}")

        chapter_name = self._tag_to_text(self.cursor.next())
        titles = self._parse_titles()

        for title in titles:
            title["payload"]["chapter_number"] = chapter_number
            title["payload"]["chapter_label"] = chapter_label
            title["payload"]["chapter_name"] = chapter_name
            chapters.append(title)

        while self.cursor.peek() is not None:
            chapter_label = self._tag_to_text(self.cursor.next())

            chapter_number_str = (re.sub(r"\s+BÖLÜM\s*$", "", chapter_label)
                                  .strip()
                                  .upper())
            chapter_number = self.CHAPTER_NUMBER_MAPPING.get(chapter_number_str)

            if chapter_number is None:
                raise ValueError(f"Unknown chapter label: {chapter_label!r}")

            chapter_name = self._tag_to_text(self.cursor.next())
            titles = self._parse_titles()

            for title in titles:
                title["payload"]["chapter_number"] = chapter_number
                title["payload"]["chapter_label"] = chapter_label
                title["payload"]["chapter_name"] = chapter_name
                chapters.append(title)

        return chapters

    def _parse_titles(self) -> list[dict]:

        titles = []

        title = self._tag_to_text(self.cursor.next())
        articles = self._parse_articles()

        for article in articles:
            article["payload"]["article_title"] = title
            titles.append(article)

        while self._is_title(self.cursor.peek()) and self._is_article(self.cursor.peek(n=2)):

            title = self._tag_to_text(self.cursor.next())
            articles = self._parse_articles()

            for article in articles:
                article["payload"]["article_title"] = title
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
            paragraph["payload"]["article_number"] = article_number

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
                                "payload": {
                                    "chunk_type": "instruction",
                                    "paragraph_number": paragraph_number,
                                    "text": f"{starting} {element} {ending}",
                                },
                                  } for element in ol_elements]

            else:

                paragraphs = [{
                                "payload": {
                                    "chunk_type": "instruction",
                                    "paragraph_number": paragraph_number,
                                    "text": f"{starting} {element}",
                                },
                                  } for element in ol_elements]

        else:

                paragraphs = [{
                    "payload": {
                        "chunk_type": "instruction",
                        "paragraph_number": paragraph_number,
                        "text": paragraph_content,
                    },
                }]

        items = self._parse_items()
        if len(items) > 0:

            paragraphs = [{
                "payload": {
                    "text": f"{paragraph["payload"]["text"]} {item["item_content"]}",
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

    @classmethod
    def _get_ordered_list_elements(cls, ol: Tag) -> list[str]:
        return [
            cls._tag_to_text(li)
            for li in ol.find_all("li")
        ]

    @classmethod
    def _get_paragraph_string(cls, paragraph: Tag) -> str:
        strings = [
            child.strip()
            for child in paragraph.contents
            if isinstance(child, NavigableString)
        ]
        text = " ".join(strings)

        cleaned_text = re.sub(r"^\s*\(\d+\)\s*", "", text)
        return cleaned_text

    @classmethod
    def _get_article_number(cls, article: Tag) -> int:
        header = article.select_one("strong")
        text = cls._tag_to_text(header)

        match = re.search(r"\d+", text)

        if match is None:
            raise ValueError("Could not extract article number")

        return int(match.group())

    @classmethod
    def _get_paragraph_number(cls, paragraph: Tag) -> int:
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

    @classmethod
    def _get_item_letter(cls, item: Tag) -> str:

        text = cls._tag_to_text(item)
        match = re.match(r"^\(([a-z]+)\)", text)

        if match is None:
            raise ValueError("Could not extract paragraph number")

        return match.group(1)

    @classmethod
    def _get_item_string(cls, item: Tag) -> str:

        text = cls._tag_to_text(item)

        cleaned_text = re.sub(r"^\s*\([a-z]+\)\s*", "", text)
        return cleaned_text

    def run(self):
        chunks = self._parse_chapters()
        self._add_main_title(chunks)
        self._add_id(chunks)
        self._add_embedding_text(chunks)

        return chunks

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