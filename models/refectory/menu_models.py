from dataclasses import dataclass, field
from enum import Enum
from tkinter import Menu


class Mealtime(Enum):
    LUNCH = "lunch"
    DINNER = "dinner"

class ServiceType(Enum):
    CANTEEN = "canteen"
    TAKEAWAY = "takeaway"

class CategoryType(Enum):
    SOUP = "soup"
    MAIN_COURSE = "main_course"
    SELECTIVE = "selective"
    VEGETARIAN = "vegetarian"
    COMPLEMENTARY = "complementary"

@dataclass
class MenuSection:
    mealtime: Mealtime
    service: ServiceType
    categories: dict[CategoryType, list[str]] = field(default_factory=dict)

    def serialize(self) -> dict:
        return {
            "mealtime": self.mealtime.value,
            "service": self.service.value,
            "categories": {
                category_type.value: meals
                for category_type, meals in self.categories.items()
            },
        }

    @classmethod
    def deserialize(cls, data: dict) -> "MenuSection":
        mealtime_value = data["mealtime"]
        service_value = data["service"]
        categories = data["categories"]

        mealtime = Mealtime(mealtime_value)
        service = ServiceType(service_value)
        categories = {
            CategoryType(category_type): meals for category_type, meals in categories.items()
        }

        return MenuSection(
            mealtime=mealtime,
            service=service,
            categories=categories
        )



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
            menu.sections.append(
                MenuSection.deserialize(section)
            )

        return menu

    def filter_by_mealtimes(self, mealtimes: list[Mealtime] | None = None) -> "Menu":

        if not mealtimes:
            return self

        filtered_menu = Menu()
        for section in self.sections:
            if section.mealtime in mealtimes:
                filtered_menu.sections.append(section)

        return filtered_menu

    def filter_by_services(self, services: list[ServiceType] | None = None) -> "Menu":

        if not services:
            return self

        filtered_menu = Menu()
        for section in self.sections:
            if section.service in services:
                filtered_menu.sections.append(section)

        return filtered_menu

    def filter_by_categories(self, categories: list[CategoryType] | None = None) -> "Menu":

        if not categories:
            return self

        filtered_menu = Menu()
        for section in self.sections:
            filtered_section = MenuSection(
                mealtime=section.mealtime,
                service=section.service,
                categories={}
            )
            for category in section.categories:
                if category in categories:
                    filtered_section.categories[category] = section.categories[category]

            filtered_menu.sections.append(filtered_section)

        return filtered_menu