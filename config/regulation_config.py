from pathlib import Path

REGULATION_COLLECTION_NAME = "regulation"
REGULATION_DB_NAME = "db"
REGULATION_DB_PATH = Path(__file__).resolve().parent.parent / REGULATION_DB_NAME

DOCUMENT_URL_MAPPING = {
    "dormitory": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
    "erasmus": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662",
    "undergraduate": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-lisans-egitim-ve-ogreti/657",
    "graduate": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-lisansustu-egitim-ve-og/656",
    "major": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661",
    "minor": "https://bogazici.edu.tr/tr/pages/bogazici-universitesi-yan-dal-programlari-yon/668",
}
DOCUMENT_TYPES = set(DOCUMENT_URL_MAPPING)