from typing import ClassVar, TypeVar
from rapidfuzz import fuzz
from config.refectory_config import MENU_CACHE_NAME, MENU_PRICE_CACHE_NAME, REFECTORY_CACHE_FOLDER
from cache.operations import read_cache
from models.refectory.menu_models import Menu, Mealtime, ServiceType, CategoryType

T = TypeVar('T')

def tool_menu(
        mealtimes: list[Mealtime] | None = None,
        services: list[ServiceType] | None = None,
        categories: list[CategoryType] | None = None,
) -> dict:

    menu_json = read_cache(
        cache_folder=REFECTORY_CACHE_FOLDER,
        cache_name=MENU_CACHE_NAME
    )
    menu = Menu.deserialize(menu_json)

    filtered_menu = (menu.
                     filter_by_mealtimes(mealtimes).
                     filter_by_services(services).
                     filter_by_categories(categories))


    return filtered_menu.serialize()

def tool_menu_price() -> dict:
    return read_cache(
        cache_folder=REFECTORY_CACHE_FOLDER,
        cache_name=MENU_PRICE_CACHE_NAME
    )

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
        Mealtime.LUNCH: {
            "öğle",
            "öğlen",
            "öğle yemeği",
            "öğlen yemeği",
            "öğle menüsü",
            "öğlen menüsü",
            "gündüz",
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

    @staticmethod
    def _extract_args(
            query: str,
            aliases: dict[T, set[str]],
            threshold: float = 80.0
            ) -> list[T]:

        words = query.split()
        extraction: list[T] = []

        index = 0
        while index < len(words):
            best_value: T | None = None
            best_score = 0.0
            best_word_count = 0

            for t, alias_set in aliases.items():
                for alias in alias_set:

                    alias_length = len(alias.split())
                    candidate_words = words[index:index + alias_length]

                    if len(candidate_words) < alias_length:
                        continue

                    candidate = " ".join(candidate_words)

                    score = fuzz.ratio(
                        candidate.casefold(),
                        alias.casefold(),
                    )

                    if score < threshold:
                        continue

                    if score > best_score or (
                        score == best_score and len(alias.split()) > best_word_count
                    ):

                        best_value = t
                        best_score = score
                        best_word_count = len(alias.split())

            if best_value:
                if best_value not in extraction:
                    extraction.append(best_value)
                index += best_word_count
            else:
                index += 1

        return extraction

    def run(self,
            query: str,
            tool_threshold: float = 85.0,
            ) -> dict:

        words = query.split()
        index = 0

        has_alias = False
        while index < len(words):

            for alias in self.MENU_PRICE_ALIASES:

                alias_length = len(alias.split())
                candidate_words = words[index:index + alias_length]

                if len(candidate_words) < alias_length:
                    continue

                candidate = " ".join(candidate_words)

                score = fuzz.ratio(
                    candidate.casefold(),
                    alias.casefold()
                )

                if score >= tool_threshold:
                    has_alias = True
                    break

            if has_alias:
                break
            else:
                index += 1

        if has_alias:
            return tool_menu_price()

        else:

            mealtimes = self._extract_args(
                query,
                self.MEALTIME_ALIASES
            )

            services = self._extract_args(
                query,
                self.SERVICE_ALIASES
            )

            categories = self._extract_args(
                query,
                self.CATEGORY_ALIASES
            )

            return tool_menu(
                mealtimes,
                services,
                categories,
            )