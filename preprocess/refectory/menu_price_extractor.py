from bs4 import BeautifulSoup, Tag
from typing import ClassVar

from models.refectory.menu_price_models import MenuPrice, PriceTable, PriceTableRow
from preprocess.soup import get_soup
from config.refectory_config import REFECTORY_CACHE_FOLDER, MENU_PRICE_CACHE_NAME
from cache.operations import write_cache

class MenuPriceExtractor:

    URL: ClassVar[str] = "https://yemekhane.bogazici.edu.tr/"

    PRICE_SUBCONTAINER_CLASS: ClassVar[str] = "subcontainer"
    PRICE_TABLE_ELEMENT: ClassVar[str] = "table"
    PRICE_TABLE_ROW_ELEMENT: ClassVar[str] = "tr"
    PRICE_AND_CATEGORY_INFO_ELEMENT: ClassVar[str] = "td"

    @staticmethod
    def _extract_price_subcontainers(soup: BeautifulSoup) -> list[Tag]:
        price_subcontainers = soup.find_all(class_=MenuPriceExtractor.PRICE_SUBCONTAINER_CLASS)[1:]

        if not price_subcontainers:
            raise ValueError("Invalid soup")

        return price_subcontainers

    @staticmethod
    def _extract_price_subcontainer_label(price_subcontainer: Tag) -> str:
        label = price_subcontainer.find("h2")

        if not label:
            raise ValueError("Invalid price subcontainer")

        return (label
                .string
                .strip())

    @staticmethod
    def _extract_price_table(price_subcontainer: Tag) -> PriceTable:

        label = MenuPriceExtractor._extract_price_subcontainer_label(price_subcontainer)

        table = price_subcontainer.find(MenuPriceExtractor.PRICE_TABLE_ELEMENT)

        if not table:
            raise ValueError("Invalid price subcontainer")

        price_table = PriceTable(label=label)
        rows = table.find_all(MenuPriceExtractor.PRICE_TABLE_ROW_ELEMENT)

        if not rows:
            raise ValueError("Invalid price table")

        for row in rows:
            row_elements = row.find_all(MenuPriceExtractor.PRICE_AND_CATEGORY_INFO_ELEMENT)

            category, price = (
                element.get_text(strip=True)
                for element in row_elements[:2]
            )

            price_table_row = PriceTableRow(
                category=category,
                price=price,
            )

            price_table.rows.append(price_table_row)

        return price_table

    @staticmethod
    def _extract_menu_price() -> MenuPrice:
        menu_price = MenuPrice()
        soup = get_soup(MenuPriceExtractor.URL)

        price_subcontainers = MenuPriceExtractor._extract_price_subcontainers(soup)

        for price_subcontainer in price_subcontainers:
            price_table = MenuPriceExtractor._extract_price_table(price_subcontainer)
            menu_price.tables.append(price_table)

        return menu_price

    @staticmethod
    def cache():
        menu_price = MenuPriceExtractor._extract_menu_price()

        write_cache(
            cache_folder=REFECTORY_CACHE_FOLDER,
            cache_name=MENU_PRICE_CACHE_NAME,
            cache_data=menu_price.serialize()
        )

