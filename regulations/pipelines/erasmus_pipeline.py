from regulations.normalizers.erasmus_normalizer import RegulationNormalizer
from regulations.pipeline import Pipeline
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

def run_pipeline(model: SentenceTransformer, client: QdrantClient) -> None:
    pipeline = Pipeline(
        url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-degisim-programlari-yon/662",
        collection_name="regulations",
        normalizer=RegulationNormalizer,
        chunker_config_name="erasmus",
        model=model,
        client=client,
    )

    pipeline.run()