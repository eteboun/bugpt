from rapidfuzz import fuzz
from typing import ClassVar

class EventRewriter:

    ALIASES: ClassVar[dict] = {

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

    def _clean_query(self, query: str, threshold: float = 80) -> str:
        words = query.split()
        result: list[str] = []
        index = 0

        time_phrases = sorted(
            self.TIME_PHRASES,
            key=lambda phrase: len(phrase.split()),
            reverse=True,
        )

        while index < len(words):

            longest_phrase_length = 0

            for phrase in time_phrases:
                phrase_length = len(phrase.split())
                candidate_words = words[index:index + phrase_length]

                if len(candidate_words) < phrase_length:
                    continue

                candidate = " ".join(candidate_words)

                score = fuzz.ratio(
                    candidate.casefold(),
                    phrase.casefold(),
                )

                if score >= threshold:
                    longest_phrase_length = max(longest_phrase_length, phrase_length)

            if longest_phrase_length > 0:
                index += longest_phrase_length
            else:
                result.append(words[index])
                index += 1

        return " ".join(result)

    def rewrite_event(self, query: str, threshold: float = 80) -> str:

        cleaned_query = self._clean_query(query)

        words = cleaned_query.split()
        result: list[str] = []
        index = 0

        aliases = sorted(
            self.ALIASES,
            key=lambda alias: len(alias.split()),
            reverse=True,
        )

        while index < len(words):
            best_alias: str | None = None
            best_score = 0.

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

                if score >= threshold and score > best_score:
                    best_alias = alias
                    best_score = score

            if best_alias is None:
                result.append(words[index])
                index += 1
            else:
                result.append(self.ALIASES[best_alias])
                index += len(best_alias.split())

        return " ".join(result)