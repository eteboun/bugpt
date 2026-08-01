import requests
from bs4 import BeautifulSoup
from dataclasses import asdict
from typing import TypeAlias

from refectory_extractor.models.menu_price_models import MenuPrice
from refectory_extractor.models.menu_models import Menu

Extraction: TypeAlias = MenuPrice | Menu

def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")

def serialize(extraction: Extraction) -> dict:
    if isinstance(extraction, Menu):
        menu_dict = asdict(extraction)

        for section in menu_dict["sections"]:
            section["mealtime"] = section["mealtime"].value
            section["service"] = section["service"].value

            section["categories"] = {
                category_type.value: meals
                for category_type, meals in section["categories"].items()
            }

        return menu_dict

    else:
        return asdict(extraction)