from bs4 import BeautifulSoup, Tag
from typing import ClassVar

from refectory_extractor.utils import get_soup, serialize
from refectory_extractor.models.menu_models import MenuSection, Mealtime, Service, CategoryType, Menu

class MenuExtractor:

    URL: ClassVar[str] = "https://yemekhane.bogazici.edu.tr/"

    BASE_FOOD_BLOCK_ID: ClassVar[str] = "block-views-yemek-block"
    MEAL_FIELD_CONTENT_CLASS: ClassVar[str] = "field-content"
    MEAL_HTML_ELEMENT: ClassVar[str] = "a"

    MENU_SECTION_ARGS_MAPPING: ClassVar[dict[str, dict]] = {
        "Öğle Yemeği": {
            "mealtime": Mealtime.LUNCH,
            "service": Service.CANTEEN
        },
        "Akşam Yemeği": {
            "mealtime": Mealtime.DINNER,
            "service": Service.CANTEEN
        },
        "Paket Öğle Yemeği": {
            "mealtime": Mealtime.LUNCH,
            "service": Service.TAKEAWAY
        },
        "Paket Akşam Yemeği": {
            "mealtime": Mealtime.DINNER,
            "service": Service.TAKEAWAY
        },
    }

    CATEGORY_TYPE_KEY_MAPPING: ClassVar[dict[str, CategoryType]] = {
        "soup": CategoryType.SOUP,
        "maincourse": CategoryType.MAIN_COURSE,
        "selective": CategoryType.SELECTIVE,
        "vegetarien": CategoryType.VEGETARIAN,
        "complementary": CategoryType.COMPLEMENTARY,
    }

    @staticmethod
    def _extract_empty_menu_section_from_food_block(food_block: Tag) -> MenuSection:
        food_block_title = (food_block
                            .find("h2")
                            .string
                            .strip())
        args = MenuExtractor.MENU_SECTION_ARGS_MAPPING.get(food_block_title)

        if not args:
            raise ValueError("Invalid food block title")

        return MenuSection(**args)

    @staticmethod
    def _extract_food_blocks(soup: BeautifulSoup) -> list[Tag]:
        return soup.select(f'[id^="{MenuExtractor.BASE_FOOD_BLOCK_ID}"]')

    @staticmethod
    def _extract_categories_from_food_block(food_block: Tag) -> dict[CategoryType, list[str]]:
        categories = {}

        food_containers = food_block.find_all(class_="food-container")

        for food_container in food_containers:
            classes = food_container["class"]
            if len(classes) < 2:
                raise ValueError("Invalid food container")

            category_type_key = classes[1]
            category_type = MenuExtractor.CATEGORY_TYPE_KEY_MAPPING.get(category_type_key)

            if not category_type:
                raise ValueError("Invalid category type")

            meal_field_content = food_container.find(class_=MenuExtractor.MEAL_FIELD_CONTENT_CLASS)

            if not meal_field_content:
                raise ValueError("Invalid meal field content")

            meal_html_elements = meal_field_content.find_all(MenuExtractor.MEAL_HTML_ELEMENT)

            if not meal_html_elements:
                raise ValueError("Invalid meal html elements")

            meals = [
                meal_html_element
                .string
                .strip()
                for meal_html_element in meal_html_elements
            ]

            categories[category_type] = meals

        return categories

    @staticmethod
    def _extract_menu_section_from_food_block(food_block: Tag) -> MenuSection:

        menu_section = MenuExtractor._extract_empty_menu_section_from_food_block(food_block)
        categories = MenuExtractor._extract_categories_from_food_block(food_block)

        menu_section.categories = categories
        return menu_section

    @staticmethod
    def _extract_menu() -> Menu:

        menu = Menu()
        soup = get_soup(MenuExtractor.URL)

        food_blocks = MenuExtractor._extract_food_blocks(soup)

        for food_block in food_blocks:
            menu_section = MenuExtractor._extract_menu_section_from_food_block(food_block)
            menu.sections.append(menu_section)

        return menu

    @staticmethod
    def call() -> dict:
        menu = MenuExtractor._extract_menu()
        serialized_menu = serialize(menu)

        return serialized_menu