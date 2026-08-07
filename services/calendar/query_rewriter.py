from typing import ClassVar
from ai.fuzzy import clean_query, rewrite_query

class QueryRewriter:

    EVENT_ALIASES: ClassVar[dict[str, str]] = {

        "add drop": "ders ekleme bırakma",
        "oryantasyon": "üniversiteyi tanıma günleri",
        "final": "dönem sonu sınavı",
        "finaller": "dönem sonu sınavları",
        "buept": "yadyok ingilizce yeterlilik sınavı",
        "ders seçimi": "çevrimiçi kayıt",
        "hazırlık": "yadyok hazırlık",
        "yaz okulu": "yaz öğretimi",
        "kayıt sistemi": "akademik kayıt sistemi",
        "ders onay": "ders onay (consent)",
        "consent sistemi": "ders onay (consent) sistemi",

    }

    MORPHOLOGICAL_ALIASES: ClassVar[dict[str, str]] = {

        "kapanıyor": "kapanışı",
        "kapanacak": "kapanışı",
        "kapanır": "kapanışı",

        "açılıyor": "açılışı",
        "açılacak": "açılışı",
        "açılır": "açılışı",

        "başvurusu": "başvuruları",
    }

    TIME_PHRASES: ClassVar[set] = {

        "ne zaman",
        "hangi tarihte",
        "hangi gün",
        "saat kaçta",
        "tarihi ne",
        "kaçta",

    }

    def _clean_query(self, query: str, threshold: float = 80.0) -> str:

        return clean_query(
            query,
            removal_terms=self.TIME_PHRASES,
            threshold=threshold
        )

    def rewrite_query(self, query: str, threshold: float = 80.0) -> str:

        query = self._clean_query(query)

        return rewrite_query(
            query,
            alias_dict=self.EVENT_ALIASES | self.MORPHOLOGICAL_ALIASES,
            threshold=threshold
        )