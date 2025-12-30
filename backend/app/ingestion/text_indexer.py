from typing import List
from qdrant_client.models import PointStruct
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.base import EmbeddingModel

COLLECTION = "text_collection"

def index_text_chunks(
    chunks: List[dict],
    embedder: EmbeddingModel,
) -> int:
    client = get_qdrant_client()

    texts = [c["text"] for c in chunks]
    vectors = embedder.embed_documents(texts)

    if len(vectors) != len(chunks):
        raise RuntimeError("Embedding count mismatch")

    points = []
    for ch, vec in zip(chunks, vectors):
        points.append(
            PointStruct(
                id=ch["id"],
                vector=vec,
                payload=ch["metadata"],
            )
        )

    client.upsert(collection_name=COLLECTION, points=points)
    return len(points)
