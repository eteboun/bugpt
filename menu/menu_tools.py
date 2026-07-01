import requests

from bs4 import BeautifulSoup
from typing import ClassVar

class MenuTools:

    URL: ClassVar[str] = "https://yemekhane.bogazici.edu.tr/"

    CATEGORY_SELECTORS: ClassVar[dict] = {
        "soup": "soup",
        "main_course": "maincourse",
        "selective": "selective",
        "vegetarian": "vegetarien",
        "complementary": "complementary",
    }

    CANTEEN_CATEGORIES: ClassVar[set] = {
        "main_course",
        "selective",
        "complementary",
        "vegetarian",
        "soup"
    }

    TAKEAWAY_CATEGORIES: ClassVar[set] = {
        "main_course",
        "selective",
        "complementary",
    }

    CATEGORY_MAPPINGS: ClassVar[dict] = {
        "canteen": CANTEEN_CATEGORIES,
        "takeaway": TAKEAWAY_CATEGORIES,
    }

    @staticmethod
    def _get_soup(url: str) -> BeautifulSoup:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    @staticmethod
    def _extract_meal_of_container(container):
        field_content = container.select_one("div.field-content")

        if field_content is None:
            return ()

        return list(
            item.get_text(strip=True)
             for item in field_content.select("a")
        )

    @staticmethod
    def _get_meals_of_containers(containers):
        size = len(containers)

        if size < 2:
            return (), ()

        else:
            lunch_meal = MenuTools._extract_meal_of_container(containers[0])
            dinner_meal = MenuTools._extract_meal_of_container(containers[1])
            if size >= 4:
                lunch_takeaway_meal = MenuTools._extract_meal_of_container(containers[2])
                dinner_takeaway_meal = MenuTools._extract_meal_of_container(containers[3])

                return lunch_meal, dinner_meal, lunch_takeaway_meal, dinner_takeaway_meal
            return lunch_meal, dinner_meal

    @staticmethod
    def _get_menu() -> list[dict]:
        soup = MenuTools._get_soup(MenuTools.URL)
        menu_scheme = {
            "lunch": {
                "canteen": {},
                "takeaway": {},
            },
            "dinner": {
                "canteen": {},
                "takeaway": {},
            }
        }
        for ctg, sel in MenuTools.CATEGORY_SELECTORS.items():
            containers = soup.select(f"div[class^='food-container {sel}']")
            if ctg in MenuTools.TAKEAWAY_CATEGORIES:
                lunch_meal, dinner_meal, lunch_takeaway_meal, dinner_takeaway_meal = MenuTools._get_meals_of_containers(containers)
                menu_scheme['lunch']["takeaway"][ctg] = lunch_takeaway_meal
                menu_scheme['dinner']["takeaway"][ctg] = dinner_takeaway_meal
            else:
                lunch_meal, dinner_meal = MenuTools._get_meals_of_containers(containers)

            menu_scheme['lunch']["canteen"][ctg] = lunch_meal
            menu_scheme['dinner']["canteen"][ctg] = dinner_meal

        menu = [
            {
                "mealtime": mealtime,
                "service": service,
                "categories": menu_scheme[mealtime][service],
            } for mealtime in menu_scheme
                for service in menu_scheme[mealtime]
        ]

        return menu

    @staticmethod
    def tool_menu():
        return MenuTools._get_menu()