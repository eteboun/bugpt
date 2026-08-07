from pathlib import Path
from contextlib import contextmanager
from qdrant_client import QdrantClient, models
from model_loader.model_loader import VECTOR_MODEL
from config.model_config import BM25_MODEL_NAME, BM25_OPTIONS

@contextmanager
def run_client(db_path: Path):
    client = QdrantClient(path=str(db_path))
    try:
        yield client
    finally:
        client.close()

def check_collection(
        client: QdrantClient,
        collection_name: str,
) -> bool:
    return client.collection_exists(collection_name)

def add_to_collection(
        client: QdrantClient,
        collection_name: str,
        chunks: list[dict]
) -> None:

    if not check_collection(client, collection_name):
        raise RuntimeError(f"Collection '{collection_name}' does not exist")

    points = []
    for chunk in chunks:
        id_ = chunk['id']
        payload = chunk['payload']
        embedding_text = chunk['embedding_text']

        points.append(
            models.PointStruct(
                id=id_,
                vector={
                    "dense": VECTOR_MODEL.encode(f"passage: {embedding_text}",
                                               normalize_embeddings=True).tolist(),

                    "bm25": models.Document(
                        text=embedding_text,
                        model=BM25_MODEL_NAME,
                        options=BM25_OPTIONS,
                    )
                },
                payload=payload
            )
        )

    client.upsert(
        collection_name=collection_name,
        points=points
    )

def create_collection(
        client: QdrantClient,
        collection_name: str,
        overwrite: bool = False,
) -> None:

    collection_config = {
        "collection_name": collection_name,
        "vectors_config": {
        "dense": models.VectorParams(
                size=VECTOR_MODEL.get_embedding_dimension(),
                distance=models.Distance.COSINE
            )
        },
        "sparse_vectors_config": {
            "bm25": models.SparseVectorParams(
                modifier=models.Modifier.IDF
            )
        }
    }

    if not client.collection_exists(collection_name):
        client.create_collection(
            **collection_config
        )

    else:
        if overwrite:
            delete_collection(client=client, collection_name=collection_name)
            client.create_collection(
                **collection_config
            )

        else:
            raise RuntimeError(f"Failed to overwrite {collection_name}")

def delete_collection(
        client: QdrantClient,
        collection_name: str,
) -> None:

    if not check_collection(client, collection_name):
        raise RuntimeError(f"Collection '{collection_name}' does not exist")

    client.delete_collection(collection_name)