from typing import ClassVar
from schemas.regulation.document_models import DocTypes
from ai.fuzzy import extract_key

class DoctypeClassifier:

    DOCTYPE_ALIASES: ClassVar[dict[DocTypes, set[str]]] = {
        DocTypes.ERASMUS: {
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

        DocTypes.DORMITORY: {
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

        DocTypes.UNDERGRADUATE: {
            "lisans",
            "lisans öğrencisi",
            "lisans eğitimi",
            "lisans programı",
            "undergraduate",
            "undergraduate program",
        },

        DocTypes.GRADUATE: {
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

        DocTypes.MAJOR: {
            "çap",
            "çift anadal",
            "çift ana dal",
            "çift anadal programı",
            "double major",
        },

        DocTypes.MINOR: {
            "yandal",
            "yan dal",
            "yandal programı",
            "yan dal programı",
            "minor program",
        },
    }

    def classify(self, query: str, threshold: float = 80.0) -> list[DocTypes]:

        doctypes: list[DocTypes] = extract_key(
            query=query,
            key_dict=self.DOCTYPE_ALIASES,
            threshold=threshold
        )

        return doctypes
