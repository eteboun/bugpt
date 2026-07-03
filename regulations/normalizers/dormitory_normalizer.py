from bs4 import Tag, BeautifulSoup
from regulations.html_parser.html_normalizer import HtmlNormalizer
from typing import override
from regulations.html_parser.html_parser_functions import ParserFunctions

class RegulationNormalizer(HtmlNormalizer):

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p')

        reached_article_26 = False
        for element in elements:
            if ParserFunctions.is_lettered_item(element):
                item_letter = ParserFunctions.get_lettered_item_letter(element)
                item_string = ParserFunctions.get_lettered_item_string(element)

                if item_letter == 'h' and item_string.startswith('Depozito:'):

                    suffix = "ifade eder."
                    cleaned_text = (ParserFunctions
                                    .get_string(element)
                                    .removesuffix(suffix) + ",")

                    element.clear()
                    element.append(cleaned_text)

                    ending = soup.new_tag('p')
                    ending.append(suffix)

                    element.insert_after(ending)

                if item_letter == 'c' and reached_article_26:

                    suffix = "tarafından verilir."

                    used_suffix = " tarafından verilir,"
                    cleaned_text = (ParserFunctions
                                    .get_string(element)
                                    .removesuffix(used_suffix) + ",")

                    element.clear()
                    element.append(cleaned_text)

                    ending = soup.new_tag('p')
                    ending.append(suffix)

                    element.insert_after(ending)
                    reached_article_26 = False

            if ParserFunctions.is_article(element) and ParserFunctions.get_article_number(element) == 17:
                items = element.find_next_siblings("p")

                first_item = items[2]
                last_item = items[3]

                first_item.string = f'1) {ParserFunctions.UNLABELED_SUB_ITEM_SELECTOR} ' + first_item.string
                last_item.string = f'2) {ParserFunctions.UNLABELED_SUB_ITEM_SELECTOR} ' + last_item.string

            if ParserFunctions.is_article(element) and ParserFunctions.get_article_number(element) == 26:
                reached_article_26 = True