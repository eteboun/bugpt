from typing import ClassVar
from bs4 import Tag, BeautifulSoup
from regulations.component_operations import ComponentOperations, TextCleaner

class Normalizer:

    letters: ClassVar[str] = "abcçdefgğhıijklmnoöprsştuüvyz"



    @staticmethod
    def _convert_ol_to_items(ol: Tag, element: Tag, soup: BeautifulSoup):

        li_list = ol.find_all('li', recursive=False)
        items = Normalizer._create_items(li_list, soup)
        for item in reversed(items):
            element.insert_after(item)
            element.insert_after('\n')
        ol.decompose()

    @staticmethod
    def _create_items(item_list: list[Tag], soup: BeautifulSoup) -> list[Tag]:
        items = []
        for idx, item in enumerate(item_list):
            text = ComponentOperations.tag_to_text(item)
            letter = Normalizer.letters[idx]

            p = soup.new_tag("p")
            p.string = f"({letter}) {text}"

            items.append(p)

        return items

    @staticmethod
    def _remove_empty_elements(regulation_container: Tag):

        elements = regulation_container.find_all("p", recursive=False)

        for element in list(elements):
            if not ComponentOperations.has_text(element):
                element.decompose()

    @staticmethod
    def _remove_hyphens(regulation_container: Tag, soup: BeautifulSoup):
        elements = regulation_container.find_all("p", recursive=False)

        for element in elements:
            if ComponentOperations.is_article(element):

                header = element.find("strong")
                text = ComponentOperations.get_string(element)

                cleared_header_string = TextCleaner.remove_hyphen(
                    ComponentOperations.tag_to_text(header)
                )

                cleared_header = soup.new_tag("strong")
                cleared_header.string = cleared_header_string

                element.clear()
                element.append(cleared_header)
                element.append(text)

            elif ComponentOperations.is_plain_text(element):
                cleared_text_string = TextCleaner.remove_hyphen(
                    ComponentOperations.tag_to_text(element)
                )

                element.clear()
                element.append(cleared_text_string)

    @staticmethod
    def _merge_strongs(tag: Tag, sep: str = " "):
        strongs = tag.find_all("strong")

        if len(strongs) <= 1:
            return

        merged_text = sep.join(
            ComponentOperations.tag_to_text(strong)
            for strong in strongs
            if ComponentOperations.tag_to_text(strong)
        )

        first_strong = strongs[0]
        first_strong.clear()
        first_strong.string = merged_text

        for strong in strongs[1:]:
            strong.decompose()

    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):
        pass

    @classmethod
    def run(cls, regulation_container: Tag, soup: BeautifulSoup):

        Normalizer._remove_empty_elements(regulation_container)
        cls._fix_container(regulation_container, soup)
        for p in regulation_container.select("p"):
            Normalizer._merge_strongs(p)
        Normalizer._remove_hyphens(regulation_container, soup)