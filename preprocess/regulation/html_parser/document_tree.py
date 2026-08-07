from bs4 import Tag
from preprocess.regulation.cursor import Cursor
from typing import ClassVar
from preprocess.regulation.html_parser.operations import Operations
from schemas.regulation.document_models import *

import re

class HtmlDocumentTree:

    DESCRIPTION_SELECTOR: ClassVar[str] = "div.inner-page__content-description"
    HEADER_SELECTOR: ClassVar[str] = "div.inner-page__content-header"

    def __init__(self, content_container: Tag):

        self.content_container = content_container

        regulation_container = content_container.select_one(self.DESCRIPTION_SELECTOR)
        elements = regulation_container.find_all(["p", "ol", "table"], recursive=False)

        cursor = Cursor(list(elements))
        self.cursor = cursor

    def _parse_chapters(self) -> list[Chapter]:

        chapters = [self._parse_chapter()]

        while self.cursor.peek() is not None:

            chapters.append(self._parse_chapter())

        return chapters

    def _parse_chapter(self) -> Chapter:

        chapter_label = Operations.tag_to_text(self.cursor.next())

        chapter_number_str = (re.sub(r"\s+BÖLÜM\s*$", "", chapter_label)
                              .strip()
                              .upper())
        number = Operations.CHAPTER_NUMBER_MAPPING[chapter_number_str]

        name = Operations.tag_to_text(self.cursor.next())
        titles = self._parse_titles()

        return Chapter(
            number=number,
            name=name,
            titles=titles,
        )

    def _parse_titles(self) -> list[Title]:

        titles = [self._parse_title()]

        while Operations.is_title(self.cursor.peek()) and Operations.is_article(self.cursor.peek(n=2)):

            titles.append(self._parse_title())

        return titles

    def _parse_title(self) -> Title:

        name = Operations.tag_to_text(self.cursor.next())
        articles = self._parse_articles()

        return Title(
            name=name,
            articles=articles,
        )
    def _parse_articles(self) -> list[Article]:

        articles = [self._parse_article()]

        while Operations.is_article(self.cursor.peek()):
            articles.append(self._parse_article())

        return articles

    def _parse_article(self) -> Article:

        article_tag = self.cursor.peek()
        number = Operations.get_article_number(article_tag)
        kind = Operations.get_article_kind(article_tag)
        paragraphs = self._parse_paragraphs()

        return Article(
            number=number,
            kind=kind,
            paragraphs=paragraphs,
        )

    def _parse_paragraphs(self) -> list[Paragraph]:

        paragraphs = [self._parse_paragraph()]

        while Operations.is_paragraph(self.cursor.peek()):

            paragraphs.append(self._parse_paragraph())

        return paragraphs

    def _parse_paragraph(self) -> Paragraph:

        paragraph_tag = self.cursor.next()
        text = Operations.get_paragraph_string(paragraph_tag)
        number = Operations.get_paragraph_number(paragraph_tag)

        return Paragraph(
            text=text,
            number=number,
            content=self._parse_paragraph_content()
        )

    def _parse_lettered_items(self, general_idx: int) -> list[Item]:

        local_idx = 0
        items = [self._parse_lettered_item(general_idx=general_idx+local_idx)]

        while Operations.is_lettered_item(self.cursor.peek()):
            local_idx += 1
            items.append(self._parse_lettered_item(general_idx=general_idx+local_idx))

        return items

    def _parse_lettered_item(self, general_idx: int) -> Item:

        item = self.cursor.next()
        label = Operations.get_lettered_item_letter(item)
        text = Operations.get_lettered_item_string(item)

        sub_items = self._parse_sub_items()

        return Item(text=text, label=label, sub_items=sub_items, general_index=general_idx)

    def _parse_item_list(self, general_idx: int) -> list[Item]:

        item_list = self.cursor.next()
        list_items = Operations.get_item_list_strings(item_list)

        return [
            Item(text=text, label=None, sub_items=[], general_index=general_idx+local_idx)
            for local_idx, text in enumerate(list_items)
        ]

    def _parse_table(self, general_idx: int, local_idx: int) -> Table:

        table = self.cursor.next()

        row_title_tags = (table
                          .find("tbody", recursive=False)
                          .find("tr", recursive=False))
        row_titles = [
            Operations.tag_to_text(td)
            for td in row_title_tags.find_all("td", recursive=False)
        ]

        rows_elements = row_title_tags.find_next_siblings("tr")
        rows = [
            Row(
                content=[
                    Operations.tag_to_text(td)
                    for td in row_element.find_all("td", recursive=False)
                ],
                local_index=local_idx
            ) for local_idx, row_element in enumerate(rows_elements)
        ]

        return Table(
            row_titles=row_titles,
            rows=rows,
            general_index=general_idx,
            local_index=local_idx
        )

    def _parse_paragraph_content(self) -> ParagraphContent:

        general_idx = 0
        table_count = 0

        content = ParagraphContent()
        while Operations.is_listed_item(self.cursor.peek()) or Operations.is_table(self.cursor.peek()):

            if Operations.is_listed_item(self.cursor.peek()):

                if Operations.is_lettered_item(self.cursor.peek()):
                    items = self._parse_lettered_items(general_idx=general_idx)

                else:
                    items = self._parse_item_list(general_idx=general_idx)

                if Operations.is_ending(self.cursor.peek()):
                    ending_tag = self.cursor.next()
                    ending = Operations.tag_to_text(ending_tag)

                    for item in items:
                        item.ending = ending

                content.items.extend(items)
                general_idx += len(items)

            else:

                table = self._parse_table(general_idx=general_idx, local_idx=table_count)
                content.tables.append(table)

                general_idx += 1
                table_count += 1

        return content

    def _parse_sub_items(self) -> list[SubItem]:

        sub_items = []

        idx = 0
        while Operations.is_sub_item(self.cursor.peek()):

            sub_item = self.cursor.next()
            text = Operations.get_sub_item_string(sub_item)
            label = Operations.get_sub_item_label(sub_item)

            sub_items.append(
                SubItem(text=text, local_index=idx, label=label)
            )

            idx += 1

        return sub_items

    def run(self) -> Document:
        chapters = self._parse_chapters()

        title_selector = self.content_container.select_one(self.HEADER_SELECTOR)
        title = Operations.tag_to_text(
            title_selector.find("h2", recursive=False)
        )

        return Document(
            name=title,
            chapters=chapters,
        )
