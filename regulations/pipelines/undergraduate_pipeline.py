from regulations.normalizers.undergraduate_normalizer import RegulationNormalizer
from regulations.pipeline import Pipeline
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def run_pipeline(model: SentenceTransformer, client: QdrantClient) -> None:
    pipeline = Pipeline(
        url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-lisans-egitim-ve-ogreti/657",
        normalizer=RegulationNormalizer,
        chunker_config_name="undergraduate",
    )

    pipeline.run(model=model,
                 client=client)
