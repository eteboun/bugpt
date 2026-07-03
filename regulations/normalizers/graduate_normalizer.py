from bs4 import Tag, BeautifulSoup
from typing import override
from regulations.html_parser.html_normalizer import HtmlNormalizer
from regulations.html_parser.html_parser_functions import ParserFunctions

class RegulationNormalizer(HtmlNormalizer):

    @staticmethod
    def _create_td(text: str, soup: BeautifulSoup) -> Tag:
        td = soup.new_tag("td")
        td.append(text)

        return td

    @staticmethod
    def _create_tr(texts: list[str], soup: BeautifulSoup) -> Tag:
        tr = soup.new_tag("tr")
        for text in texts:
            td = RegulationNormalizer._create_td(text, soup)
            tr.append(td)

        return tr

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        first_p = regulation_container.find('p', recursive=False)
        h2 = regulation_container.find('h2', recursive=False)

        first_p.decompose()
        h2.decompose()

        first_chapter_tag = regulation_container.find('p', recursive=False)
        chapter_number = first_chapter_tag.find("strong", recursive=False)
        chapter_name = chapter_number.find_next_sibling("strong", recursive=False)

        chapter_number_tag = soup.new_tag('p')
        chapter_number_tag.append(chapter_number)

        chapter_name_tag = soup.new_tag('p')
        chapter_name_tag.append(chapter_name)

        first_chapter_tag.insert_after(chapter_name_tag)
        first_chapter_tag.insert_after(chapter_number_tag)
        first_chapter_tag.decompose()

        elements = regulation_container.find_all('p', recursive=False)
        for element in list(elements):
            if len(element.find_all("u", recursive=False)) == 3:

                table = soup.new_tag("table")
                body = soup.new_tag("tbody")

                texts = [ParserFunctions.tag_to_text(u)
                         for u in element.find_all("u", recursive=False)]
                title_row = RegulationNormalizer._create_tr(texts, soup)
                body.append(title_row)

                current_row = element
                for row_idx in range(7):

                    row_tag = current_row.find_next_sibling("p")
                    current_row.decompose()

                    texts = (ParserFunctions
                             .tag_to_text(row_tag)
                             .split())

                    if row_idx == 6:
                        texts.append('-')

                    row = RegulationNormalizer._create_tr(texts, soup)
                    body.append(row)

                    current_row = row_tag

                table.append(body)

                current_row.insert_after(table)
                current_row.decompose()

            elif len(element.find_all("u", recursive=False)) == 2:

                table = soup.new_tag("table")
                body = soup.new_tag("tbody")

                texts = [ParserFunctions.tag_to_text(u)
                         for u in element.find_all("u", recursive=False)]
                title_row = RegulationNormalizer._create_tr(texts, soup)
                body.append(title_row)

                current_row = element
                for row_idx in range(12):

                    row_tag = current_row.find_next_sibling("p")
                    current_row.decompose()

                    text_pieces = (ParserFunctions
                                     .tag_to_text(row_tag)
                                     .split())
                    sign = text_pieces[0]
                    description = " ".join(text_pieces[1:])
                    texts = [sign, description]

                    row = RegulationNormalizer._create_tr(texts, soup)
                    body.append(row)

                    current_row = row_tag

                table.append(body)

                current_row.insert_after(table)
                current_row.decompose()

            if "(4 Değişik : RG-20/07/2017-30129)" in ParserFunctions.tag_to_text(element):
                element.string = element.string.replace("(4 Değişik : RG-20/07/2017-30129)", "(4)")

            if ParserFunctions.is_article(element) and ParserFunctions.get_article_number(element) == 32:
                text = ParserFunctions.get_paragraph_string(element)
                text = text.replace("(1 Değişik : RG-20/07/2017-30129)", "(1)")

                for string in element.find_all(string=True, recursive=False):
                    string.extract()

                element.append(text)
