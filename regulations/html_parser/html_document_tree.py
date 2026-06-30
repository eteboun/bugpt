from bs4 import Tag
from regulations.utils import Cursor
from typing import ClassVar
from regulations.html_parser.html_parser_functions import ParserFunctions
from regulations.document_structure import *

import re

class HtmlDocumentTree:

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    def __init__(self, content_container: Tag):

        self.content_container = content_container

        regulation_container = content_container.select_one(self.DESCRIPTION_SELECTOR)
        elements = regulation_container.find_all(["p", "ol"], recursive=False)

        cursor = Cursor(list(elements))
        self.cursor = cursor

    def _parse_chapters(self) -> list[Chapter]:

        chapters = [self._parse_chapter()]

        while self.cursor.peek() is not None:

            chapters.append(self._parse_chapter())

        return chapters

    def _parse_chapter(self) -> Chapter:

        chapter_label = ParserFunctions.tag_to_text(self.cursor.next())

        chapter_number_str = (re.sub(r"\s+BÖLÜM\s*$", "", chapter_label)
                              .strip()
                              .upper())
        number = ParserFunctions.CHAPTER_NUMBER_MAPPING[chapter_number_str]

        name = ParserFunctions.tag_to_text(self.cursor.next())
        titles = self._parse_titles()

        return Chapter(
            number=number,
            name=name,
            titles=titles,
        )

    def _parse_titles(self) -> list[Title]:

        titles = [self._parse_title()]

        while ParserFunctions.is_title(self.cursor.peek()) and ParserFunctions.is_article(self.cursor.peek(n=2)):

            titles.append(self._parse_title())

        return titles

    def _parse_title(self) -> Title:

        name = ParserFunctions.tag_to_text(self.cursor.next())
        articles = self._parse_articles()

        return Title(
            name=name,
            articles=articles,
        )
    def _parse_articles(self) -> list[Article]:

        articles = [self._parse_article()]

        while ParserFunctions.is_article(self.cursor.peek()):
            articles.append(self._parse_article())

        return articles

    def _parse_article(self) -> Article:

        article_tag = self.cursor.peek()
        number = ParserFunctions.get_article_number(article_tag)
        kind = ParserFunctions.get_article_kind(article_tag)
        paragraphs = self._parse_paragraphs()

        return Article(
            number=number,
            kind=kind,
            paragraphs=paragraphs,
        )

    def _parse_paragraphs(self) -> list[Paragraph]:

        paragraphs = [self._parse_paragraph()]

        while ParserFunctions.is_paragraph(self.cursor.peek()):

            paragraphs.append(self._parse_paragraph())

        return paragraphs

    def _parse_paragraph(self) -> Paragraph:

        paragraph_tag = self.cursor.next()
        text = ParserFunctions.get_paragraph_string(paragraph_tag)
        number = ParserFunctions.get_paragraph_number(paragraph_tag)

        return Paragraph(
            text=text,
            number=number,
            item_groups=self._parse_item_groups()
        )

    def _parse_lettered_items(self) -> list[Item]:

        idx = 0
        items = [self._parse_lettered_item(idx=idx)]

        while ParserFunctions.is_lettered_item(self.cursor.peek()):
            idx += 1
            items.append(self._parse_lettered_item(idx))

        return items

    def _parse_lettered_item(self, idx: int) -> Item:

        item = self.cursor.next()
        label = ParserFunctions.get_lettered_item_letter(item)
        text = ParserFunctions.get_lettered_item_string(item)

        sub_items = self._parse_sub_items()

        return Item(text=text, label=label, sub_items=sub_items, local_index=idx)

    def _parse_item_list(self) -> list[Item]:

        item_list = self.cursor.next()
        list_items = ParserFunctions.get_item_list_strings(item_list)

        return [
            Item(text=text, label=None, local_index=idx, sub_items=[])
            for idx, text in enumerate(list_items)
        ]

    def _parse_item_groups(self) -> list[ItemGroup]:

        idx = 0
        item_groups = []

        while ParserFunctions.is_lettered_item(self.cursor.peek()) or ParserFunctions.is_item_list(self.cursor.peek()):

            if ParserFunctions.is_lettered_item(self.cursor.peek()):
                items = self._parse_lettered_items()

            else:
                items = self._parse_item_list()

            if ParserFunctions.is_sub_item_or_ending(self.cursor.peek()):
                ending_tag = self.cursor.next()
                ending = ParserFunctions.tag_to_text(ending_tag)

                item_groups.append(
                    ItemGroup(items=items, ending=ending, local_index=idx)
                )

            else:
                item_groups.append(
                    ItemGroup(items=items, ending=None, local_index=idx)
                )

            idx += 1

        return item_groups

    def _parse_sub_items(self) -> list[SubItem]:

        sub_items = []

        if (ParserFunctions.is_sub_item_or_ending(self.cursor.peek())
                and ParserFunctions.is_sub_item_or_ending(self.cursor.peek(2))):

            idx = 0
            while (ParserFunctions.is_sub_item_or_ending(self.cursor.peek())
                   and ParserFunctions.is_sub_item_or_ending(self.cursor.peek(2))):

                sub_item = self.cursor.next()
                text = ParserFunctions.tag_to_text(sub_item)

                sub_items.append(
                    SubItem(text=text, local_index=idx)
                )

                idx += 1

            sub_item = self.cursor.next()
            text = ParserFunctions.tag_to_text(sub_item)

            sub_items.append(
                SubItem(text=text, local_index=idx)
            )

        return sub_items

    def run(self) -> Document:
        chapters = self._parse_chapters()

        title_selector = self.content_container.select_one(self.HEADER_SELECTOR)
        title = ParserFunctions.tag_to_text(
            title_selector.select_one("h2")
        )

        return Document(
            title=title,
            chapters=chapters,
        )
