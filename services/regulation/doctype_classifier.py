from rapidfuzz import fuzz
from typing import ClassVar

class DoctypeClassifier:

    DOCTYPE_ALIASES: ClassVar[dict[str, set[str]]] = {
        "erasmus": {
            "erasmus",
            "erasmus programı",
            "erasmus değişim programı",
            "exchange program",
            "öğrenci değişim programı",
            "uluslararası değişim programı",
            "study abroad",
            "yurt dışında eğitim",
            "yurtdışında eğitim",
        },

        "dormitory": {
            "öğrenci yurdu",
            "üniversite yurdu",
            "boğaziçi yurdu",
            "yurt başvurusu",
            "yurt yerleştirmesi",
            "yurtta kalma",
            "dormitory",
            "student dormitory",
            "student housing",
            "residence hall",
        },

        "undergraduate": {
            "lisans",
            "lisans öğrencisi",
            "lisans eğitimi",
            "lisans programı",
            "undergraduate",
            "undergraduate program",
        },

        "graduate": {
            "lisansüstü",
            "lisansüstü eğitim",
            "lisansüstü program",
            "yüksek lisans",
            "yüksek lisans programı",
            "doktora",
            "doktora programı",
            "graduate program",
            "master program",
            "phd program",
        },

        "double_major": {
            "çap",
            "çift anadal",
            "çift ana dal",
            "çift anadal programı",
            "double major",
        },

        "minor": {
            "yandal",
            "yan dal",
            "yandal programı",
            "yan dal programı",
            "minor program",
        },
    }

    def classify(self, query: str, threshold: float = 80.) -> list[str]:

        classified_doctypes: list[str] = []
        words = query.split()
        index = 0

        while index < len(words):
            best_doctype: str | None = None
            best_alias: str | None = None
            best_score = 0

            for doctype, aliases in self.DOCTYPE_ALIASES.items():
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
                        best_score = score
                        best_doctype = doctype
                        best_alias = alias

            if best_doctype:
                classified_doctypes.append(best_doctype)
                index += len(best_alias.split())
            else:
                index += 1

        return classified_doctypes
