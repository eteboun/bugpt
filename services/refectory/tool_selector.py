from typing import ClassVar, Literal
from ai.fuzzy import extract_key, extract_keys, match
from schemas.refectory.menu_models import Mealtime, ServiceType, CategoryType, MenuFilter

class ToolSelector:

    MENU_PRICE_ALIASES: ClassVar[set[str]] = {
        "fiyat",
        "kaç tl",
        "kaç lira",
        "ne kadar",
        "ücret",
        "price"
    }

    MEALTIME_ALIASES: ClassVar[dict[Mealtime, set[str]]] = {
        Mealtime.BREAKFAST: {
            "kahvaltı",
            "kahvaltıda",
            "kahvaltı yemeği",
            "kahvaltı menüsü",
            "sabah",
            "sabah yemeği",
            "sabah menüsü",
            "breakfast",
            "breakfast menu",
            "gündüz"
        },

        Mealtime.LUNCH: {
            "öğle",
            "öğlen",
            "öğle yemeği",
            "öğlen yemeği",
            "öğle menüsü",
            "öğlen menüsü",
            "lunch",
            "lunch menu"
        },

        Mealtime.DINNER: {
            "akşam",
            "akşam yemeği",
            "akşam menüsü",
            "gece yemeği",
            "dinner",
            "dinner menu",
            "supper"
        }
    }

    SERVICE_ALIASES: ClassVar[dict[ServiceType, set[str]]] = {
        ServiceType.CANTEEN: {
            "yemekhane",
            "yemekhane menüsü",
            "yerinde yemek",
            "tabldot",
            "canteen",
            "cafeteria",
            "dining hall"
        },
        ServiceType.TAKEAWAY: {
            "paket",
            "paket yemek",
            "paket servis",
            "paket menü",
            "al götür",
            "al-götür",
            "takeaway",
            "take away",
            "takeout",
            "to go"
        }
    }

    CATEGORY_ALIASES: ClassVar[dict[CategoryType, set[str]]] = {
        CategoryType.SOUP: {
            "soup",
            "çorba",
            "çorbalar",
        },

        CategoryType.MAIN_COURSE: {
            "main course",
            "main_course",
            "ana yemek",
            "ana yemekler",
            "ana öğün",
            "esas yemek",
        },

        CategoryType.SELECTIVE: {
            "selective",
            "seçmeli",
            "seçmeli yemek",
            "seçenek",
            "alternatif",
            "alternatif yemek",
        },

        CategoryType.VEGETARIAN: {
            "vegan",
            "vegetarian",
            "vejetaryen",
            "vejeteryan",
            "etsiz",
            "sebze yemeği",
            "vejetaryen yemek",
            "vejeteryan yemek",
        },

        CategoryType.COMPLEMENTARY: {
            "complementary",
            "tamamlayıcı",
            "tamamlayıcı yemek",
            "yan yemek",
            "yardımcı yemek",
            "garnitür",
            "pilav",
            "makarna",
        },
    }

    def _select_tool(self, query: str, threshold: float = 85.0) -> Literal["menu", "menu_price"]:

        match_ = match(
            query,
            aliases=self.MENU_PRICE_ALIASES,
            threshold=threshold,
        )

        if match_:
            return "menu_price"
        else:
            return "menu"

    def _extract_menu_args(self, query: str, threshold: float = 80.0) -> MenuFilter:

        mealtime = extract_key(
            query,
            key_dict=self.MEALTIME_ALIASES,
            threshold=threshold
        )

        service = extract_key(
            query,
            key_dict=self.SERVICE_ALIASES,
            threshold=threshold
        )

        categories = extract_keys(
            query,
            key_dict=self.CATEGORY_ALIASES,
            threshold=threshold
        )

        filter_ = MenuFilter(
            mealtime=mealtime,
            service=service,
            categories=categories,
        )

        return filter_

    def run(self,
            query: str,
            tool_threshold: float = 85.0,
            extraction_threshold: float = 80.0,
            ) -> dict:

        selected_tool: Literal["menu", "menu_price"] = self._select_tool(query, threshold=tool_threshold)
        if selected_tool == "menu":
            args = {
                "filter_": self._extract_menu_args(query, threshold=extraction_threshold)
            }
        else:
            args = {}

        return {
            "tool": selected_tool,
            "args": args,
        }