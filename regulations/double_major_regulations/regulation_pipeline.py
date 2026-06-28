from regulations.pipeline import Pipeline
from regulations.double_major_regulations.regulation_normalizer import RegulationNormalizer

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
)