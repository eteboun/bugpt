from regulations.pipeline import Pipeline
from regulations.double_major_regulations.regulation_normalizer import RegulationNormalizer
import json

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
)

print(json.dumps(pipeline._get_html_tree(), indent=4, ensure_ascii=False))
#remove hyphen eklenecek