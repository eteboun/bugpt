from regulations.pipeline import Pipeline
from regulations.normalizers.dormitory_normalizer import RegulationNormalizer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import json
def run_pipeline() -> None:
    pipeline = Pipeline(
        url="https://bogazici.edu.tr/tr/pages/bogazici-universitesi-ogrenci-yurtlari-yonerg/669",
        collection_name="regulations",
        normalizer=RegulationNormalizer,
        chunker_config_name="dormitory",
    )

    print(
        json.dumps(
            [c.as_dict() for c in pipeline._get_chunks()]
        , indent=2, ensure_ascii=False
        )
    )

    #pipeline.run(model=model,
     #            client=client)


run_pipeline()