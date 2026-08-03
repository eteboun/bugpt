from dataclasses import dataclass, field
from enum import Enum

class Mealtime(Enum):
    LUNCH = "lunch"
    DINNER = "dinner"

class Service(Enum):
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
    service: Service
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

@dataclass
class Menu:
    sections: list[MenuSection] = field(default_factory=list)

    def serialize(self) -> dict:
        return {
            "sections": [
                s.serialize() for s in self.sections
            ]
        }