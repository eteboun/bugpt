from bs4 import BeautifulSoup, Tag
from typing import ClassVar
from datetime import date
from calendar import monthrange
from enum import StrEnum
from dataclasses import dataclass
from abc import ABC, abstractmethod

from preprocess.soup import get_soup
from schemas.refectory.menu_calendar_models import Mealtime, ServiceType, CategoryType, Menu, MainMeal, Breakfast, MenuSection, MenuCalendar
from config.cache_names import MENU_CALENDAR_CACHE_NAME, REFECTORY_CACHE_FOLDER
from cache.operations import write_cache

class MainMealLabel(StrEnum):
    LUNCH_CANTEEN = "öğle yemeği"
    DINNER_CANTEEN = "akşam yemeği"
    LUNCH_TAKEAWAY = "paket öğle yemeği"
    DINNER_TAKEAWAY = "paket akşam yemeği"

class FoodBlockClassSuffixes(StrEnum):
    SOUP = "ccorba"
    MAIN_COURSE = "anaa-yemek"
    SELECTIVE = "aperatiff"
    VEGETARIAN = "vejetarien"
    COMPLEMENTARY = "yardimciyemek"

    MEALTIME_LABEL = "yemek-saati"

@dataclass
class MainMealLabelInfo:
    mealtime: Mealtime
    service: ServiceType

class MealExtractor(ABC):

    URL: ClassVar[str]

    DATE_BLOCK_FIELD: ClassVar[str] = "data-date"
    DATE_BLOCK_CLASS: ClassVar[str] = "single-day"

    FOOD_HTML_ELEMENT: ClassVar[str] = "a"

    MEAL_LABEL_CLASS_BASE: ClassVar[str] = "views-field-field-"

    CLASS_SUFFIX_CATEGORY_TYPE_MAPPING: ClassVar[dict[FoodBlockClassSuffixes, CategoryType]] = {
        FoodBlockClassSuffixes.SOUP: CategoryType.SOUP,
        FoodBlockClassSuffixes.MAIN_COURSE: CategoryType.MAIN_COURSE,
        FoodBlockClassSuffixes.SELECTIVE: CategoryType.SELECTIVE,
        FoodBlockClassSuffixes.VEGETARIAN: CategoryType.VEGETARIAN,
        FoodBlockClassSuffixes.COMPLEMENTARY: CategoryType.COMPLEMENTARY,
    }

    def _get_class(self, class_suffix: FoodBlockClassSuffixes) -> str:
        return self.MEAL_LABEL_CLASS_BASE + class_suffix

    def _extract_date_block(self, soup: BeautifulSoup, date_: date) -> Tag:
        block = soup.find(
            "td",
            attrs={
                self.DATE_BLOCK_FIELD: str(date_),
                "class": self.DATE_BLOCK_CLASS,
            },
        )
        if not block:
            raise ValueError("Invalid date")

        return block

    @staticmethod
    def _extract_item_blocks(date_block: Tag) -> list[Tag]:
        return date_block.find_all("div", class_="item")

    def _extract_food_block(self, item_block: Tag, class_suffix: FoodBlockClassSuffixes) -> Tag:
        class_ = self._get_class(class_suffix)
        return item_block.find(class_=class_)

    def _extract_foods(self, food_block: Tag) -> list[str]:
        return [
            element.get_text(strip=True)
            for element in food_block.find_all(self.FOOD_HTML_ELEMENT)
        ]

    @abstractmethod
    def get_sections(self, date_: date) -> list[MenuSection]:
        ...

class MainMealExtractor(MealExtractor):

    MAIN_MEAL_LABEL_MAPPING: ClassVar[dict[
        MainMealLabel, MainMealLabelInfo
    ]] = {
        MainMealLabel.LUNCH_CANTEEN: MainMealLabelInfo(
            mealtime=Mealtime.LUNCH,
            service=ServiceType.CANTEEN,
        ),
        MainMealLabel.DINNER_CANTEEN: MainMealLabelInfo(
            mealtime=Mealtime.DINNER,
            service=ServiceType.CANTEEN,
        ),
        MainMealLabel.LUNCH_TAKEAWAY: MainMealLabelInfo(
            mealtime=Mealtime.LUNCH,
            service=ServiceType.TAKEAWAY,
        ),
        MainMealLabel.DINNER_TAKEAWAY: MainMealLabelInfo(
            mealtime=Mealtime.DINNER,
            service=ServiceType.TAKEAWAY,
        ),
    }

    def _extract_main_meal_label(self, item_block: Tag) -> MainMealLabel:

        class_ = self._get_class(class_suffix=FoodBlockClassSuffixes.MEALTIME_LABEL)

        label_tag = item_block.find("div", class_=class_)
        if not label_tag:
            raise ValueError("Invalid date block")

        label = (label_tag
                 .get_text(strip=True)
                 .casefold())

        return MainMealLabel(label)

    def _extract_main_meal_label_info(self, main_meal_label: MainMealLabel) -> MainMealLabelInfo:

        label_info = self.MAIN_MEAL_LABEL_MAPPING.get(
            main_meal_label
        )

        if not label_info:
            raise ValueError("Invalid main meal label")

        return label_info

    def _extract_categories(self, item_block: Tag) -> dict[CategoryType, list[str]]:

        categories = {}
        for class_suffix, category in self.CLASS_SUFFIX_CATEGORY_TYPE_MAPPING.items():
            food_block = self._extract_food_block(item_block=item_block, class_suffix=class_suffix)

            foods = self._extract_foods(food_block=food_block)
            if not foods:
                continue

            categories[category] = foods

        return categories

    def _extract_main_meals(self, date_: date) -> list[MainMeal]:
        main_meals: list[MainMeal] = []

        soup = get_soup(url=self.URL)
        date_block = self._extract_date_block(soup=soup, date_=date_)
        item_blocks = self._extract_item_blocks(date_block=date_block)

        for item_block in item_blocks:
            label = self._extract_main_meal_label(item_block=item_block)
            label_info = self._extract_main_meal_label_info(main_meal_label=label)

            mealtime = label_info.mealtime
            service = label_info.service
            categories = self._extract_categories(item_block=item_block)

            main_meals.append(MainMeal(
                mealtime=mealtime,
                service=service,
                categories=categories,
            ))

        return main_meals

    def get_sections(self, date_: date) -> list[MainMeal]:
        canteen_extractor = CanteenMainMealExtractor()
        takeaway_extractor = TakeawayMainMealExtractor()

        sections = (canteen_extractor.get_sections(date_=date_)
                    + takeaway_extractor.get_sections(date_=date_))

        return sections

class CanteenMainMealExtractor(MainMealExtractor):
    URL = "https://yemekhane.bogazici.edu.tr/aylik-menu"

    def get_sections(self, date_: date) -> list[MainMeal]:
        return self._extract_main_meals(date_=date_)

class TakeawayMainMealExtractor(MainMealExtractor):
    URL = "https://yemekhane.bogazici.edu.tr/paket-menu"

    def get_sections(self, date_: date) -> list[MainMeal]:
        return self._extract_main_meals(date_=date_)

class BreakfastExtractor(MealExtractor):
    URL = "https://yemekhane.bogazici.edu.tr/kahvalti-menu/"

    def _extract_breakfast_foods(self, item_block: Tag) -> list[str]:

        foods: list[str] = []
        for class_suffix, category in self.CLASS_SUFFIX_CATEGORY_TYPE_MAPPING.items():
            food_block = self._extract_food_block(item_block=item_block, class_suffix=class_suffix)

            if not food_block:
                continue

            extracted_foods = self._extract_foods(food_block=food_block)
            foods += extracted_foods

        return foods

    def get_sections(self, date_: date) -> list[Breakfast]:

        soup = get_soup(self.URL)
        date_block = self._extract_date_block(soup=soup, date_=date_)
        item_blocks = self._extract_item_blocks(date_block=date_block)

        if not item_blocks:
            return []

        item_block = next(iter(
            item_blocks
        ))

        foods = self._extract_breakfast_foods(item_block=item_block)

        return [
            Breakfast(
                service=ServiceType.CANTEEN,
                foods=foods
            ),
            Breakfast(
                service=ServiceType.TAKEAWAY,
                foods=[]
            )
        ]

class MenuExtractor:

    def __init__(self):
        self.breakfast_extractor = BreakfastExtractor()
        self.main_meal_extractor = MainMealExtractor()

    def _extract_menu(self, date_: date) -> Menu:

        sections = (self.breakfast_extractor.get_sections(date_=date_)
                    + self.main_meal_extractor.get_sections(date_=date_))

        return Menu(
            sections=sections
        )

    def _extract_menu_calendar(self) -> MenuCalendar:

        today = date.today()

        dates = [
            date(today.year, today.month, day)
            for day in range(1, monthrange(today.year, today.month)[1] + 1)
        ]

        menus = [
            self._extract_menu(date_=date_)
            for date_ in dates
        ]

        return MenuCalendar(
            calendar=dict(
                zip(dates, menus)
            )
        )

    def cache(self) -> None:

        menu_calendar = self._extract_menu_calendar()
        serialized_menu_calendar = menu_calendar.serialize()

        write_cache(
            cache_folder=REFECTORY_CACHE_FOLDER,
            cache_name=MENU_CALENDAR_CACHE_NAME,
            cache_data=serialized_menu_calendar
        )

e = MenuExtractor()
e.cache()