from bs4 import Tag, BeautifulSoup
from regulations.html_parser.html_normalizer import HtmlNormalizer
from regulations.html_parser.html_parser_functions import ParserFunctions
from typing import ClassVar, override

class RegulationNormalizer(HtmlNormalizer):

    INCOMPATIBLE_TITLES: ClassVar[set] = {"Dayanak",
                                          "Çift ana dal Programında Başarı Şartı, Ders Yükü ve Süre",
                                          "Başvuru Süreci ve Kabul",
                                          "Çift ana dal Programından Ayrılma ve Çıkarılma"}


    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p', recursive=False)
        for element in list(elements):
            if ParserFunctions.is_article(element):
                if ParserFunctions.tag_to_text(
                        element.find("strong")
                ) in RegulationNormalizer.INCOMPATIBLE_TITLES:

                    title_tag = element.find("strong")

                    article_tag = title_tag.find_next_sibling("strong")
                    paragraph_text = ParserFunctions.get_string(element)

                    title_p = soup.new_tag('p')
                    title_p.append(title_tag)

                    article_strong = soup.new_tag('strong')
                    article_strong.string = ParserFunctions.tag_to_text(article_tag)

                    article_p = soup.new_tag('p')
                    article_p.append(article_strong)
                    article_p.append(paragraph_text)

                    element.insert_after(article_p)
                    element.insert_after(title_p)

                    element.decompose()