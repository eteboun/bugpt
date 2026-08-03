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

@dataclass
class Menu:
    sections: list[MenuSection] = field(default_factory=list)