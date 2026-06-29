from regulations.pipeline import Pipeline
from regulations.double_major_regulations.regulation_normalizer import RegulationNormalizer
from regulations.chunker_config import ChunkerConfig

config = ChunkerConfig()

config.add_option(
    chapter_number=1,
    article_number=4,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=1,
    article_number=7,
    paragraph_number=1,
    item_merge="none",
)

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-cift-ana-dal-programlar/661",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
    chunker_config=config,
)
