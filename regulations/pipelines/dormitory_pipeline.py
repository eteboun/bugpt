from regulations.pipeline import Pipeline
from regulations.normalizers.dormitory_normalizer import RegulationNormalizer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def run_pipeline(model: SentenceTransformer, client: QdrantClient) -> None:
    pipeline = Pipeline(
        url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
        normalizer=RegulationNormalizer,
        chunker_config_name="dormitory",
    )

    pipeline.run(model=model,
                 client=client)


