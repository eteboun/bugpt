from bs4 import Tag, NavigableString, BeautifulSoup
from regulations.normalizer import Normalizer
from regulations.component_operations import TextCleaner, ComponentOperations
from typing import ClassVar, override

class RegulationNormalizer(Normalizer):

    NON_BOLD_TITLES: ClassVar[set] = {"Değerlendirme ve Yerleştirme",
                                      "Yürürlük",
                                      "Yürütme"}

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p', recursive=False)
        for element in list(elements):
            if ComponentOperations.is_article(element):
                article_number = ComponentOperations.get_article_number(element)

                match article_number:
                    case 4 | 8 | 13:

                        ol = element.find_next_sibling("ol")
                        RegulationNormalizer._convert_ol_to_items(
                            element=element,
                            ol=ol,
                            soup=soup,
                        )

                    case 9:

                        ol = element.find_next_sibling("ol")
                        p = ol.find_next_sibling("p")
                        main_ol = p.find_next_sibling("ol")

                        RegulationNormalizer._convert_ol_to_items(
                            element=element,
                            ol=main_ol,
                            soup=soup,
                        )

                        ol.decompose()
                        p.decompose()

                    case 26:
                        header = element
                        p = header.find_next_sibling("p")

                        for child in header.contents:
                            if isinstance(child, NavigableString) and child.strip():
                                child.replace_with(
                                    TextCleaner.add_period(
                                        ComponentOperations.get_string(header)
                                    )
                                )
                                break

                        p.string = TextCleaner.add_period(
                            ComponentOperations.tag_to_text(p),
                        )

                    case _:
                        continue

            elif (not ComponentOperations.is_title(element)
                  and ComponentOperations.tag_to_text(element) in RegulationNormalizer.NON_BOLD_TITLES):

                strong = soup.new_tag("strong")
                strong.string = ComponentOperations.tag_to_text(element)

                element.clear()
                element.append(strong)

