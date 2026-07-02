from bs4 import Tag, BeautifulSoup
from typing import override
from regulations.html_parser.html_parser_functions import ParserFunctions
from regulations.html_parser.html_normalizer import HtmlNormalizer

class RegulationNormalizer(HtmlNormalizer):

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        first_p = regulation_container.find('p', recursive=False)
        h2 = regulation_container.find('h2', recursive=False)

        first_p.decompose()
        h2.decompose()

        elements = regulation_container.find_all("p", recursive=False)
        for element in list(elements):
            if ParserFunctions.is_article(element):
                article_number = ParserFunctions.get_article_number(element)

                if article_number == 24:

                    title_name = "İşaretler"
                    strong = element.find("strong", recursive=False)

                    strong.string = strong.string.removeprefix(title_name)
                    title_tag = soup.new_tag("p")

                    title = soup.new_tag("strong")
                    title.string = title_name

                    title_tag.append(title)
                    element.insert_before(title_tag)