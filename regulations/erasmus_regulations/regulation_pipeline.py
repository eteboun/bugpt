import json

from regulations.pipeline import Pipeline
from regulations.erasmus_regulations.regulation_normalizer import RegulationNormalizer

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
)