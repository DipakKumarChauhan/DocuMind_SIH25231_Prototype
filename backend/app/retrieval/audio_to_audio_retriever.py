from app.asr.orchestrator import transcribe_audio
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.db.qdrant_client import get_qdrant_client
from qdrant_client.models import Filter, FieldCondition, MatchValue

def retrieve_similar_audio(
        audio_url,
        owner_id,
        top_k=5,
):
    # transcribe_audio returns dict with 'transcript' key
    result = transcribe_audio(audio_url)
    transcript = result.get("transcript", "")
    
    if not transcript or len(transcript.strip()) < 5:
        return []  # Empty or too short transcript
    
    embedder = HFBgeM3Embedder()
    vec = embedder.embed_query(transcript)

    client = get_qdrant_client()
    result = client.query_points(
        collection_name = "audio_collection",
        query=vec,
        using = "transcript",
        query_filter= Filter(
            must= [
                FieldCondition(
                    key="owner_id",
                    match= MatchValue(value= owner_id),
                )
            ]
        ),
        limit=top_k,
        with_payload= True,
    )

    return [
        {
            "audio_url": p.payload["audio_url"],
            "score": float(p.score),
            "transcript": p.payload["transcript"],
        }
        for p in result.points
    ]



