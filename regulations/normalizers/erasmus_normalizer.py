from bs4 import Tag, BeautifulSoup
from regulations.html_parser.normalizer import HtmlNormalizer
from regulations.html_parser.operations import Operations
from typing import ClassVar, override

class RegulationNormalizer(HtmlNormalizer):

    NON_BOLD_TITLES: ClassVar[set] = {"Değerlendirme ve Yerleştirme",
                                      "Yürürlük",
                                      "Yürütme"}

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all("p", recursive=False)
        for element in list(elements):
            if Operations.is_article(element):
                article_number = Operations.get_article_number(element)

                if article_number == 9:

                    ol_1 = element.find_next_sibling("ol")
                    p = ol_1.find_next_sibling("p")
                    ol_2 = p.find_next_sibling("ol")

                    last_li = ol_1.find_all("li", recursive=False)[-1]
                    last_li.string += " " + p.string

                    next_li_list = ol_2.find_all("li", recursive=False)
                    for li in next_li_list:
                        ol_1.append(li)

                    ol_2.decompose()
                    p.decompose()

            elif (not Operations.is_title(element)
                  and Operations.tag_to_text(element) in RegulationNormalizer.NON_BOLD_TITLES):

                strong = soup.new_tag("strong")
                strong.string = Operations.tag_to_text(element)

                element.clear()
                element.append(strong)

