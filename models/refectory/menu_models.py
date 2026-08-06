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

    def filter(self,
               mealtimes: list[Mealtime],
               services: list[ServiceType],
               categories: list[CategoryType]
               ) -> "Menu":

        if mealtimes:
            mealtime_filtered_sections = [
                section for section in self.sections
                if section.mealtime in mealtimes
            ]
        else:
            mealtime_filtered_sections = self.sections

        if services:
            service_filtered_sections = [
                section for section in mealtime_filtered_sections
                if section.service in services
            ]
        else:
            service_filtered_sections = mealtime_filtered_sections

        if categories:
            category_filtered_sections = []
            for section in service_filtered_sections:
                filtered_section = MenuSection(
                    mealtime=section.mealtime,
                    service=section.service,
                    categories={}
                )
                for category in categories:
                    filtered_section.categories[category] = section.categories.get(category, [])

                category_filtered_sections.append(filtered_section)
        else:
            category_filtered_sections = service_filtered_sections

        return Menu(
            sections=category_filtered_sections
        )