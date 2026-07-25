from bs4 import Tag, BeautifulSoup
from regulations.html_parser.normalizer import HtmlNormalizer
from typing import override, ClassVar
from regulations.html_parser.operations import Operations

class DormitoryNormalizer(HtmlNormalizer):

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p')

        reached_article_26 = False
        for element in elements:
            if Operations.is_lettered_item(element):
                item_letter = Operations.get_lettered_item_letter(element)
                item_string = Operations.get_lettered_item_string(element)

                if item_letter == 'h' and item_string.startswith('Depozito:'):

                    suffix = "ifade eder."
                    cleaned_text = (Operations
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
                    cleaned_text = (Operations
                                    .get_string(element)
                                    .removesuffix(used_suffix) + ",")

                    element.clear()
                    element.append(cleaned_text)

                    ending = soup.new_tag('p')
                    ending.append(suffix)

                    element.insert_after(ending)
                    reached_article_26 = False

            if Operations.is_article(element) and Operations.get_article_number(element) == 17:
                items = element.find_next_siblings("p")

                first_item = items[2]
                last_item = items[3]

                first_item.string = f'1) {Operations.UNLABELED_SUB_ITEM_SELECTOR} ' + first_item.string
                last_item.string = f'2) {Operations.UNLABELED_SUB_ITEM_SELECTOR} ' + last_item.string

            if Operations.is_article(element) and Operations.get_article_number(element) == 26:
                reached_article_26 = True

class GraduateNormalizer(HtmlNormalizer):

    @staticmethod
    def _create_td(text: str, soup: BeautifulSoup) -> Tag:
        td = soup.new_tag("td")
        td.append(text)

        return td

    @staticmethod
    def _create_tr(texts: list[str], soup: BeautifulSoup) -> Tag:
        tr = soup.new_tag("tr")
        for text in texts:
            td = GraduateNormalizer._create_td(text, soup)
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

                texts = [Operations.tag_to_text(u)
                         for u in element.find_all("u", recursive=False)]
                title_row = GraduateNormalizer._create_tr(texts, soup)
                body.append(title_row)

                current_row = element
                for row_idx in range(7):

                    row_tag = current_row.find_next_sibling("p")
                    current_row.decompose()

                    texts = (Operations
                             .tag_to_text(row_tag)
                             .split())

                    if row_idx == 6:
                        texts.append('-')

                    row = GraduateNormalizer._create_tr(texts, soup)
                    body.append(row)

                    current_row = row_tag

                table.append(body)

                current_row.insert_after(table)
                current_row.decompose()

            elif len(element.find_all("u", recursive=False)) == 2:

                table = soup.new_tag("table")
                body = soup.new_tag("tbody")

                texts = [Operations.tag_to_text(u)
                         for u in element.find_all("u", recursive=False)]
                title_row = GraduateNormalizer._create_tr(texts, soup)
                body.append(title_row)

                current_row = element
                for row_idx in range(12):

                    row_tag = current_row.find_next_sibling("p")
                    current_row.decompose()

                    text_pieces = (Operations
                                   .tag_to_text(row_tag)
                                   .split())
                    sign = text_pieces[0]
                    description = " ".join(text_pieces[1:])
                    texts = [sign, description]

                    row = GraduateNormalizer._create_tr(texts, soup)
                    body.append(row)

                    current_row = row_tag

                table.append(body)

                current_row.insert_after(table)
                current_row.decompose()

            if "(4 Değişik : RG-20/07/2017-30129)" in Operations.tag_to_text(element):
                element.string = element.string.replace("(4 Değişik : RG-20/07/2017-30129)", "(4)")

            if Operations.is_article(element) and Operations.get_article_number(element) == 32:
                text = Operations.get_paragraph_string(element)
                text = text.replace("(1 Değişik : RG-20/07/2017-30129)", "(1)")

                for string in element.find_all(string=True, recursive=False):
                    string.extract()

                element.append(text)

class MajorNormalizer(HtmlNormalizer):

    INCOMPATIBLE_TITLES: ClassVar[set] = {"Dayanak",
                                          "Çift ana dal Programında Başarı Şartı, Ders Yükü ve Süre",
                                          "Başvuru Süreci ve Kabul",
                                          "Çift ana dal Programından Ayrılma ve Çıkarılma"}


    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        elements = regulation_container.find_all('p', recursive=False)
        for element in list(elements):
            if Operations.is_article(element):
                if Operations.tag_to_text(
                        element.find("strong")
                ) in MajorNormalizer.INCOMPATIBLE_TITLES:

                    title_tag = element.find("strong")
                    article_tag = title_tag.find_next_sibling("strong")

                    if article_tag.find("strong", recursive=False):
                        article_tag.unwrap()

                    new_title_tag = title_tag.extract()

                    title_p = soup.new_tag('p')
                    title_p.append(new_title_tag)

                    element.insert_before(title_p)

class MinorNormalizer(HtmlNormalizer):

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
                ) in MinorNormalizer.INCOMPATIBLE_TITLES:

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

class UndergraduateNormalizer(HtmlNormalizer):

    @override
    @staticmethod
    def _fix_container(regulation_container: Tag, soup: BeautifulSoup):

        first_p = regulation_container.find('p', recursive=False)
        h2 = regulation_container.find('h2', recursive=False)

        first_p.decompose()
        h2.decompose()

        elements = regulation_container.find_all("p", recursive=False)
        for element in list(elements):
            if Operations.is_article(element):
                article_number = Operations.get_article_number(element)

                if article_number == 24:

                    title_name = "İşaretler"
                    strong = element.find("strong", recursive=False)

                    strong.string = strong.string.removeprefix(title_name)
                    title_tag = soup.new_tag("p")

                    title = soup.new_tag("strong")
                    title.string = title_name

                    title_tag.append(title)
                    element.insert_before(title_tag)

class ErasmusNormalizer(HtmlNormalizer):

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
                  and Operations.tag_to_text(element) in ErasmusNormalizer.NON_BOLD_TITLES):

                strong = soup.new_tag("strong")
                strong.string = Operations.tag_to_text(element)

                element.clear()
                element.append(strong)
