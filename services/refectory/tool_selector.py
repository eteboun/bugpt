from typing import ClassVar
from rapidfuzz import fuzz

class ToolSelector:

    MENU_PRICE_ALIASES: ClassVar[set[str]] = {
        "fiyat",
        "menü fiyatı",
        "yemek fiyatı",
        "öğle yemeği fiyatı",
        "akşam yemeği fiyatı",
        "kaç tl",
        "kaç lira",
        "ne kadar",
        "ücret",
        "price",
    }

    MEALTIME_ALIASES: ClassVar[dict[str, set[str]]] = {
        "lunch": {
            "öğle",
            "öğlen",
            "öğle yemeği",
            "öğlen yemeği",
            "öğle menüsü",
            "öğlen menüsü",
            "gündüz",
            "lunch",
            "lunch menu",
        },

        "dinner": {
            "akşam",
            "akşam yemeği",
            "akşam menüsü",
            "gece yemeği",
            "dinner",
            "dinner menu",
            "supper",
        },
    }

    SERVICE_ALIASES: ClassVar[dict[str, set[str]]] = {
        "canteen": {
            "yemekhane",
            "yemekhane menüsü",
            "yerinde yemek",
            "tabldot",
            "canteen",
            "cafeteria",
            "dining hall",
        },
        "takeaway": {
            "paket",
            "paket yemek",
            "paket servis",
            "paket menü",
            "al götür",
            "al-götür",
            "takeaway",
            "take away",
            "takeout",
            "to go",
        },
    }

    def select(self,
               query: str,
               tool_threshold: float = 85.,
               mealtime_threshold: float = 80.,
               service_threshold: float = 80.
               ) -> dict:

        words = query.split()
        index = 0

        tool: str | None = None
        while index < len(words):

            for alias in self.MENU_PRICE_ALIASES:

                alias_length = len(alias.split())
                candidate_words = words[index:index + alias_length]

                if len(candidate_words) < alias_length:
                    continue

                candidate = " ".join(candidate_words)

                score = fuzz.ratio(
                    candidate.casefold(),
                    query.casefold()
                )

                if score >= tool_threshold:
                    tool = "menu_price"

        if tool:
            return {
                "tool": tool,
                "args": {}
            }

        else:
            mealtimes = []
            services = []

            index = 0
            while index < len(words):

                for mealtime, aliases in self.MEALTIME_ALIASES.items():
                    for alias in aliases:

                        alias_length = len(alias.split())
                        candidate_words = words[index:index + alias_length]

                        if len(candidate_words) < alias_length:
                            continue

                        candidate = " ".join(candidate_words)

                        score = fuzz.ratio(
                            candidate.casefold(),
                            alias.casefold(),
                        )

                        if score >= mealtime_threshold:
                            mealtimes.append(mealtime)
                            break

            index = 0
            while index < len(words):

                for service, aliases in self.SERVICE_ALIASES.items():
                    for alias in aliases:

                        alias_length = len(alias.split())
                        candidate_words = words[index:index + alias_length]

                        if len(candidate_words) < alias_length:
                            continue

                        candidate = " ".join(candidate_words)

                        score = fuzz.ratio(
                            candidate.casefold(),
                            alias.casefold(),
                        )

                        if score >= service_threshold:
                            services.append(service)
                            break

            return {
                "tool": tool,
                "args": {
                    "mealtimes": mealtimes,
                    "services": services,
                },
            }
