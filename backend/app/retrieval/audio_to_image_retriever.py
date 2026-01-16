from app.asr.orchestrator import transcribe_audio
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict

def retrieve_image_from_audio(
        audio_url: str,
        owner_id: str,
        top_k=5,
) :
    # transcribe_audio returns dict with 'transcript' key
    result_dict = transcribe_audio(audio_url)
    transcript = result_dict.get("transcript", "")
    if not transcript or len(transcript.strip()) < 5:
        return []
    
    embedder = HFBgeM3Embedder()
    text_vec = embedder.embed_query(transcript)

    client = get_qdrant_client()
    result = client.query_points(
        collection_name="image_collection",
        query=text_vec,
        using="ocr",
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
            "image_url": p.payload["image_url"],
            "score": float(p.score),
            "file_id": p.payload.get("file_id", "unknown"),
            "text": p.payload.get("ocr_text", ""),
        }
        for p in result.points
    ]


