from regulations.normalizers.minor_normalizer import RegulationNormalizer
from regulations.pipeline import Pipeline
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def run_pipeline(model: SentenceTransformer, client: QdrantClient) -> None:
    pipeline = Pipeline(
        url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-yan-dal-programlari-yon/668",
        normalizer=RegulationNormalizer,
        chunker_config_name="minor",
    )

    pipeline.run(model=model,
                 client=client)
