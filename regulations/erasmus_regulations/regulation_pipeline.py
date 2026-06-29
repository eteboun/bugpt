from regulations.pipeline import Pipeline
from regulations.erasmus_regulations.regulation_normalizer import RegulationNormalizer
from regulations.chunker_config import ChunkerConfig
import json

config = ChunkerConfig()

config.add_option(
    chapter_number=1,
    article_number=4,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=3,
    article_number=8,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=3,
    article_number=13,
    paragraph_number=1,
    item_merge="partial",
    item_group_sizes=(3, 1)
)

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
    chunker_config=config
)

print(json.dumps(pipeline._get_chunks(), indent=4, ensure_ascii=False))
