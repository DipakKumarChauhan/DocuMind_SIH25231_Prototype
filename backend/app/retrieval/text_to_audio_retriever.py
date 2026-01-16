from qdrant_client.models import Filter, FieldCondition, MatchValue, VectorParams, Distance, PayloadSchemaType, SparseVectorParams
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.db.qdrant_client import get_qdrant_client

AUDIO_COLLECTION = "audio_collection"
_embedder = None

def retrieve_audio_from_text(
        query: str,
        owner_id:str,
        top_k=5,
):
    embedder = _embedder or HFBgeM3Embedder()
    vec = embedder.embed_query(query)
    client = get_qdrant_client()
    result = client.query_points(
        collection_name=AUDIO_COLLECTION,
        query = vec,
        using = "transcript",
        query_filter= Filter(
            must=[
                FieldCondition(
                    key="owner_id",
                    match= MatchValue(value= owner_id),
                )
            ]
        ),
        limit= top_k,
        with_payload= True,
    )
    result_list = []

    for p in result.points:
        result_list.append({
           "id": p.id,
            "score": float(p.score),
            "audio_url": p.payload["audio_url"],
            "transcript": p.payload["transcript"],
            "timestamps": p.payload.get("timestamps"),
        })
    
    return result_list

    # return [
    #     {
    #         "id": p.id,
    #         "score": float(p.score),
    #         "audio_url": p.payload["audio_url"],
    #         "transcript": p.payload["transcript"],
    #         "timestamps": p.payload.get("timestamps"),
    #     }
    #     for p in result.points
    # ]



