from regulations.pipeline import Pipeline
from regulations.dormitory_regulations.regulation_normalizer import RegulationNormalizer

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
)

