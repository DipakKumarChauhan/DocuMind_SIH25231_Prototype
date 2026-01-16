from typing import List, Dict
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.image.orchestrator import embed_image
# from app.embeddings.image.clip_text import embed_text_clip
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder


def retrieve_audio_from_image(
        image_url: str,
        owner_id: str,
        top_k=5,
):
    emb  =  embed_image(image_url)
    ocr_text =  emb.get("ocr_text")
    if not ocr_text:
        return []
    
    text_embedder = HFBgeM3Embedder()
    text_vec = text_embedder.embed_query(ocr_text)

    client = get_qdrant_client()
    results = client.query_points(
        collection_name="audio_collection",
        query=text_vec,
        using="transcript",
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match=MatchValue(value=owner_id),
                )
            ]
        ),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "audio_url": p.payload["audio_url"],
            "score": float(p.score),
            "transcript": p.payload["transcript"],
        }
        for p in results.points
    ]




