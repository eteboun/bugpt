from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal
from datetime import date

class Mealtime(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"

class ServiceType(StrEnum):
    CANTEEN = "canteen"
    TAKEAWAY = "takeaway"

class CategoryType(StrEnum):
    SOUP = "soup"
    MAIN_COURSE = "main_course"
    SELECTIVE = "selective"
    VEGETARIAN = "vegetarian"
    COMPLEMENTARY = "complementary"

@dataclass
class MenuSection:
    mealtime: Mealtime
    service: ServiceType

    def serialize(self) -> dict:
        return {
            "mealtime": self.mealtime.value,
            "service": self.service.value,
        }

    @staticmethod
    def deserialize(data: dict) -> tuple[Mealtime, ServiceType]:
        return (
            Mealtime(data["mealtime"]),
            ServiceType(data["service"]),
        )

@dataclass
class MainMeal(MenuSection):

    mealtime: Literal[Mealtime.LUNCH, Mealtime.DINNER]
    categories: dict[CategoryType, list[str]] = field(default_factory=dict)

    def serialize(self) -> dict:
        data = super().serialize()
        data["categories"] = {
                category.value: foods
                for category, foods in self.categories.items()
            }

        return data
    @classmethod
    def deserialize(cls, data: dict) -> "MainMeal":

        mealtime, service = super().deserialize(data)
        if mealtime == Mealtime.BREAKFAST:
            raise ValueError("Breakfast is not a main meal")

        return cls(
            mealtime=mealtime,
            service=service,
            categories={
                CategoryType(category): foods
                for category, foods in data["categories"].items()
            }
        )

@dataclass
class Breakfast(MenuSection):

    mealtime: Literal[Mealtime.BREAKFAST] = field(
        init=False,
        default=Mealtime.BREAKFAST
    )
    foods: list[str]

    empty_food_label: str = "no foods available"

    def serialize(self) -> dict:
        data = super().serialize()
        data["foods"] = self.foods if self.foods else self.empty_food_label

        return data

    @classmethod
    def deserialize(cls, data: dict) -> "Breakfast":

        mealtime, service = super().deserialize(data)
        if mealtime != Mealtime.BREAKFAST:
            raise ValueError("Lunch or Dinner is not a breakfast")

        foods = [] \
            if data["foods"] == cls.empty_food_label \
            else data["foods"]

        return cls(
            service=service,
            foods=foods,
        )

@dataclass
class CategoryFilterResult(MenuSection):
    categories: dict[CategoryType, list[str]] = field(default_factory=dict)

    def serialize(self) -> dict:

        data = super().serialize()
        data["categories"] = {
                category.value: foods
                for category, foods in self.categories.items()
            }

        return data

    @classmethod
    def deserialize(cls, data: dict) -> "CategoryFilterResult":
        mealtime, service = super().deserialize(data)
        return cls(
            mealtime = mealtime,
            service = service,
            categories = {
                CategoryType(category): foods for category, foods in data["categories"].items()
            }
        )

@dataclass
class MenuFilter:
    mealtime: Mealtime | None
    service: ServiceType | None
    categories: list[CategoryType]

@dataclass
class Menu:
    sections: list[MenuSection] = field(default_factory=list)

    def serialize(self) -> dict:
        return {
            "sections": [
                s.serialize() for s in self.sections
            ]
        }

    @classmethod
    def deserialize(cls, data: dict) -> "Menu":
        menu = Menu()
        sections = data["sections"]

        for section in sections:
            mealtime = Mealtime(
                section["mealtime"]
            )

            if mealtime == Mealtime.BREAKFAST:
                menu_section = Breakfast.deserialize(section)

            else:
                menu_section = MainMeal.deserialize(section)

            menu.sections.append(
                menu_section
            )

        return menu

    def filter(self, filter_: MenuFilter) -> "Menu":

        if filter_.mealtime:
            mealtime_filtered_sections = [
                section for section in self.sections
                if section.mealtime == filter_.mealtime
            ]
        else:
            mealtime_filtered_sections = self.sections

        if filter_.service:
            service_filtered_sections = [
                section for section in mealtime_filtered_sections
                if section.service == filter_.service
            ]
        else:
            service_filtered_sections = mealtime_filtered_sections

        if filter_.categories:
            category_filtered_sections = []
            for section in service_filtered_sections:
                filtered_section = CategoryFilterResult(
                    mealtime=section.mealtime,
                    service=section.service,
                )

                if isinstance(section, Breakfast):
                    categories = dict.fromkeys(filter_.categories)
                else:
                    assert isinstance(section, MainMeal)
                    categories = {
                        category: section.categories.get(category) for category in filter_.categories
                    }

                filtered_section.categories = categories
                category_filtered_sections.append(filtered_section)
        else:
            category_filtered_sections = service_filtered_sections

        return Menu(
            sections=category_filtered_sections
        )

@dataclass
class MenuCalendar:
    calendar: dict[date, Menu] = field(default_factory=dict)

    def serialize(self) -> dict:
        return {
            "calendar": {
                str(date_): menu.serialize()
                for date_, menu in self.calendar.items()
            }
        }

    @classmethod
    def deserialize(cls, data: dict) -> "MenuCalendar":
        return cls(
            calendar={
                date.fromisoformat(date_): Menu.deserialize(menu) for date_, menu in data["calendar"].items()
            }
        )

    def search(self, date_: date) -> Menu:
        return self.calendar.get(date_)