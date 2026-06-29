from regulations.pipeline import Pipeline
from regulations.dormitory_regulations.regulation_normalizer import RegulationNormalizer
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
    chapter_number=2,
    article_number=5,
    paragraph_number=1,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=6,
    paragraph_number=2,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=7,
    paragraph_number=2,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=8,
    paragraph_number=1,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=10,
    paragraph_number=1,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=11,
    paragraph_number=3,
    item_merge="full",
)

config.add_option(
    chapter_number=2,
    article_number=12,
    paragraph_number=1,
    item_merge="full",
)

config.add_option(
    chapter_number=3,
    article_number=13,
    paragraph_number=1,
    item_merge="none",
    include_paragraph_content=False,
)

config.add_option(
    chapter_number=3,
    article_number=14,
    paragraph_number=2,
    item_merge="full",
)

config.add_option(
    chapter_number=3,
    article_number=15,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=3,
    article_number=16,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=3,
    article_number=16,
    paragraph_number=2,
    item_merge="full",
)

config.add_option(
    chapter_number=3,
    article_number=16,
    paragraph_number=3,
    item_merge="full",
)

config.add_option(
    chapter_number=3,
    article_number=17,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=3,
    article_number=18,
    paragraph_number=1,
    item_merge="none",
)

config.add_option(
    chapter_number=4,
    article_number=21,
    paragraph_number=1,
    item_merge="full",
)

config.add_option(
    chapter_number=4,
    article_number=22,
    paragraph_number=2,
    item_merge="none",
)

config.add_option(
    chapter_number=4,
    article_number=23,
    paragraph_number=2,
    item_merge="none",
)

config.add_option(
    chapter_number=4,
    article_number=24,
    paragraph_number=2,
    item_merge="none",
)

config.add_option(
    chapter_number=4,
    article_number=25,
    paragraph_number=2,
    item_merge="none",
)

config.add_option(
    chapter_number=4,
    article_number=26,
    paragraph_number=1,
    item_merge="none",
)

pipeline = Pipeline(
    url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
    collection_name="regulations",
    normalizer=RegulationNormalizer,
    chunker_config=config,
)

print(json.dumps(pipeline._get_html_tree(), indent=4, ensure_ascii=False))


