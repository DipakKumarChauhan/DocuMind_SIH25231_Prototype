import math
from typing import List,Dict
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.image.orchestrator import embed_image
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder


TEXT_COLLECTION = 'text_collection'

_text_embedder = None
STOPWORDS = {
    "the","a","an","and","or","of","to","in","on","for","with",
    "is","are","was","were","it","this","that","these","those",
}


    # Using Lazy Loaded Singleton design pattern to load the text embedder only when needed
    # The embedder is created only once, It is reused everywhere, It is created only when needed
    # By this we avoid unnecessary resource consumption if the embedder is not used it wont' be loaded
    #  
def _get_text_embedder():
    global _text_embedder
    if _text_embedder is None:
        _text_embedder = HFBgeM3Embedder()
    return _text_embedder


def _token_overlap(query: str, candidate: str) -> float:
    qt = {t for t in query.lower().split() if t not in STOPWORDS}
    ct = {t for t in candidate.lower().split() if t not in STOPWORDS}
    if not qt or not ct:
        return 0.0
    inter = len(qt & ct)
    return inter / math.sqrt(len(qt) * len(ct))

def retrieve_text_from_image(
        image_url:str,
        owner_id:str,
    top_k:int =5,
    min_score: float | None = None,
)-> List[Dict]:
    client = get_qdrant_client()
    emb =  embed_image(image_url)

    ocr_text = emb.get("ocr_text")
    if not ocr_text:
        return []
    text_embedder = _get_text_embedder()
    query_vector = text_embedder.embed_query(ocr_text)

    owner_filter =  Filter(
        must = [
            FieldCondition(
                key = "owner_id",
                match = MatchValue(value = owner_id)
            )
        ]
    )

    result = client.query_points(
        collection_name = TEXT_COLLECTION,
        query = query_vector,
        using = "dense",
        query_filter = owner_filter,
        limit = top_k,
        with_payload = True
    )

    # output=[]

    # for p in result.points:
    #     output.append({
    #     "id": p.id,
    #     "score": float(p.score),
    #     "text": p.payload.get("text"),
    #     "filename": p.payload.get("filename"),
    #     "page" : p.payload.get("page"),
    #     "source": p.payload.get("source"),

    #     })

    # return output
    # Light rerank: prefer lexical overlap with the OCR text to avoid semantically loose matches.
    reranked = []
    for p in result.points:
        payload_text = p.payload.get("text") or ""
        overlap = _token_overlap(ocr_text, payload_text) if len(ocr_text.split()) >= 5 else 0.0
        combined = 0.9 * float(p.score) + 0.1 * overlap
        reranked.append({
            "id": p.id,
            "score": float(p.score),
            "combined_score": combined,
            "text": payload_text,
            "filename": p.payload.get("filename"),
            "page": p.payload.get("page"),
            "source": p.payload.get("source"),
        })

    reranked.sort(key=lambda x: x["combined_score"], reverse=True)
    return reranked[:top_k]