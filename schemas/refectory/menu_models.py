from dataclasses import dataclass, field
from enum import StrEnum

class Mealtime(StrEnum):
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
class MenuFilter:
    mealtimes: list[Mealtime]
    services: list[ServiceType]
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
            menu.sections.append(
                MenuSection.deserialize(section)
            )

        return menu

    def filter(self, filter_: MenuFilter) -> "Menu":

        if filter_.mealtimes:
            mealtime_filtered_sections = [
                section for section in self.sections
                if section.mealtime in filter_.mealtimes
            ]
        else:
            mealtime_filtered_sections = self.sections

        if filter_.services:
            service_filtered_sections = [
                section for section in mealtime_filtered_sections
                if section.service in filter_.services
            ]
        else:
            service_filtered_sections = mealtime_filtered_sections

        if filter_.categories:
            category_filtered_sections = []
            for section in service_filtered_sections:
                filtered_section = MenuSection(
                    mealtime=section.mealtime,
                    service=section.service,
                    categories={}
                )
                for category in filter_.categories:
                    filtered_section.categories[category] = section.categories.get(category, [])

                category_filtered_sections.append(filtered_section)
        else:
            category_filtered_sections = service_filtered_sections

        return Menu(
            sections=category_filtered_sections
        )