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

    return pipeline._get_document_tree()

print(run_pipeline(2,2))
