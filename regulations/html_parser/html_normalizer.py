from bs4 import Tag, BeautifulSoup
from regulations.html_parser.html_parser_functions import ParserFunctions
import re

class HtmlNormalizer:

    @staticmethod
    def _remove_empty_elements(regulation_container: Tag):

        elements = regulation_container.find_all("p", recursive=False)

        for element in list(elements):
            if not ParserFunctions.has_text(element):
                element.decompose()

    @staticmethod
    def remove_hyphen(element: str) -> str:
        return (re.sub(r"^\s*[-–]+\s*|\s*[-–]+\s*$", "", element)
                .strip())

    @staticmethod
    def _remove_hyphens(regulation_container: Tag, soup: BeautifulSoup):
        elements = regulation_container.find_all("p", recursive=False)

        for element in elements:
            if ParserFunctions.is_article(element):

                header = element.find("strong")
                text = ParserFunctions.get_string(element)

                cleared_header_string = HtmlNormalizer.remove_hyphen(
                    ParserFunctions.tag_to_text(header)
                )

                cleared_text_string = HtmlNormalizer.remove_hyphen(text)

                cleared_header = soup.new_tag("strong")
                cleared_header.string = cleared_header_string

                element.clear()
                element.append(cleared_header)
                element.append(cleared_text_string)

            elif ParserFunctions.is_plain_text(element):
                cleared_text_string = HtmlNormalizer.remove_hyphen(
                    ParserFunctions.tag_to_text(element)
                )

                element.clear()
                element.append(cleared_text_string)

    @staticmethod
    def _merge_strongs(tag: Tag, sep: str = " "):
        strongs = tag.find_all("strong")

        if len(strongs) <= 1:
            return

        merged_text = sep.join(
            ParserFunctions.tag_to_text(strong)
            for strong in strongs
            if ParserFunctions.tag_to_text(strong)
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

        HtmlNormalizer._remove_empty_elements(regulation_container)
        cls._fix_container(regulation_container, soup)
        for p in regulation_container.find_all("p", recursive=False):
            HtmlNormalizer._merge_strongs(p)
        HtmlNormalizer._remove_hyphens(regulation_container, soup)