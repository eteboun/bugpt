from bs4 import Tag
from regulations.utils import Cursor
from typing import ClassVar
from regulations.component_operations import ComponentOperations

import re

class HtmlDocumentTree:

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    def __init__(self, content_container: Tag):

        self.content_container = content_container

        regulation_container = content_container.select_one(self.DESCRIPTION_SELECTOR)
        elements = regulation_container.find_all("p", recursive=False)

        cursor = Cursor(list(elements))
        self.cursor = cursor

    def _parse_chapters(self) -> list[dict]:

        chapters = [self._parse_chapter()]

        while self.cursor.peek() is not None:

            chapters.append(self._parse_chapter())

        return chapters

    def _parse_chapter(self) -> dict:

        chapter_label = ComponentOperations.tag_to_text(self.cursor.next())

        chapter_number_str = (re.sub(r"\s+BÖLÜM\s*$", "", chapter_label)
                              .strip()
                              .upper())
        chapter_number = ComponentOperations.CHAPTER_NUMBER_MAPPING[chapter_number_str]

        chapter_name = ComponentOperations.tag_to_text(self.cursor.next())
        titles = self._parse_titles()

        chapter = {
            "chapter_number": chapter_number,
            "chapter_name": chapter_name,
            "titles": titles,
        }

        return chapter

    def _parse_titles(self) -> list[dict]:

        titles = [self._parse_title()]

        while ComponentOperations.is_title(self.cursor.peek()) and ComponentOperations.is_article(self.cursor.peek(n=2)):

            titles.append(self._parse_title())

        return titles

    def _parse_title(self) -> dict:

        title_name = ComponentOperations.tag_to_text(self.cursor.next())
        articles = self._parse_articles()

        title = {
            "title_name": title_name,
            "articles": articles,
        }

        return title

    def _parse_articles(self) -> list[dict]:

        articles = [self._parse_article()]

        while ComponentOperations.is_article(self.cursor.peek()):
            articles.append(self._parse_article())

        return articles

    def _parse_article(self) -> dict:

        article_tag = self.cursor.peek()
        article_number = ComponentOperations.get_article_number(article_tag)
        paragraphs = self._parse_paragraphs()

        article = {
            "article_number": article_number,
            "paragraphs": paragraphs,
        }
        return article

    def _parse_paragraphs(self) -> list[dict]:

        paragraphs = [self._parse_paragraph()]

        while ComponentOperations.is_paragraph(self.cursor.peek()):

            paragraphs.append(self._parse_paragraph())

        return paragraphs

    def _parse_paragraph(self) -> dict:

        paragraph_tag = self.cursor.next()
        paragraph_content = ComponentOperations.get_paragraph_string(paragraph_tag)
        paragraph_number = ComponentOperations.get_paragraph_number(paragraph_tag)

        paragraph = {"paragraph_number": paragraph_number,
                     "paragraph_content": paragraph_content,
                     "item_groups": self._parse_item_groups()}

        return paragraph

    def _parse_item_groups(self) -> list[dict]:

        item_groups = []

        items = []
        while ComponentOperations.is_item(self.cursor.peek()):
            item = self.cursor.next()
            item_letter = ComponentOperations.get_item_letter(item)
            item_content = ComponentOperations.get_item_string(item)

            sub_items = self._parse_sub_items()

            items.append({
                "item_letter": item_letter,
                "item_content": item_content,
                "sub_items": sub_items,
            })

        if items:
            if ComponentOperations.is_sub_item_or_ending(self.cursor.peek()):
                ending_tag = self.cursor.next()
                ending = ComponentOperations.tag_to_text(ending_tag)

                item_group = {
                    "items": items,
                    "ending": ending,
                }
                item_groups.append(item_group)
                item_groups.extend(self._parse_item_groups())

            else:
                item_group = {
                    "items": items,
                    "ending": None,
                }
                item_groups.append(item_group)

        return item_groups

    def _parse_sub_items(self) -> list[str]:

        sub_items = []

        if (ComponentOperations.is_sub_item_or_ending(self.cursor.peek())
                and ComponentOperations.is_sub_item_or_ending(self.cursor.peek(2))):

            while (ComponentOperations.is_sub_item_or_ending(self.cursor.peek())
                and ComponentOperations.is_sub_item_or_ending(self.cursor.peek(2))):

                sub_item = self.cursor.next()
                text = ComponentOperations.tag_to_text(sub_item)

                sub_items.append(text)

            sub_item = self.cursor.next()
            text = ComponentOperations.tag_to_text(sub_item)

            sub_items.append(text)

        return sub_items

    def run(self) -> dict:
        chapters = self._parse_chapters()

        title_selector = self.content_container.select_one(self.HEADER_SELECTOR)
        main_title = ComponentOperations.tag_to_text(
            title_selector.select_one("h2")
        )

        return {
            "main_title": main_title,
            "chapters": chapters,
        }
