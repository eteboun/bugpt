from bs4 import Tag, BeautifulSoup
from regulations.html_parser.normalizer import HtmlNormalizer
from regulations.html_parser.operations import Operations
from typing import ClassVar, override

class RegulationNormalizer(HtmlNormalizer):

    INCOMPATIBLE_TITLES: ClassVar[set] = {"Dayanak",
                                          "Yan Dal Programı",
                                          "Başvuru Süreci ve Kabul",
                                          "Yandal Programına Devam, Ders Yükü, Başarı Şartı ve Süre",
                                          "Mezuniyet"}

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p', recursive=False)
        for element in list(elements):
            if Operations.is_article(element):
                if Operations.tag_to_text(
                        element.find("strong")
                ) in RegulationNormalizer.INCOMPATIBLE_TITLES:

                    title_tag = element.find("strong")
                    article_tag = title_tag.find_next_sibling("strong")

                    if article_tag.find("strong", recursive=False):
                        article_tag.unwrap()

                    new_title_tag = title_tag.extract()

                    title_p = soup.new_tag('p')
                    title_p.append(new_title_tag)

                    element.insert_before(title_p)

                elif Operations.get_article_number(element) == 13:

                    header = element.find("strong")
                    string = Operations.get_paragraph_string(element)

                    header.extract()
                    element.clear()

                    header.string = header.string.removesuffix("(1)")
                    string = f"(1) {string}"

                    element.append(header)
                    element.append(string)
