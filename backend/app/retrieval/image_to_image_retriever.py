import math
from typing import List, Dict
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.image.orchestrator import embed_image
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder

IMAGE_COLLECTION = "image_collection"
_text_embedder = None  # Lazy init to reuse across calls
_ocr_cache = {}
MAX_OCR_CACHE = 1000


def _get_text_embedder() -> HFBgeM3Embedder:
    global _text_embedder
    if _text_embedder is None:
        _text_embedder = HFBgeM3Embedder()
    return _text_embedder


def _cosine(a: List[float], b: List[float]) -> float:
    # Embeddings are normalized; dot product equals cosine similarity.
    return sum(x * y for x, y in zip(a, b)) if a and b else 0.0


def _normalize(v: List[float]) -> List[float]:
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v] if norm > 0 else v


def _good_ocr(text: str) -> bool:
    # Ignore tiny or empty OCR snippets; they are too noisy for reranking.
    return bool(text) and len(text.split()) >= 5


def _embed_cached(text: str, embedder: HFBgeM3Embedder) -> List[float]:
    if text not in _ocr_cache:
        if len(_ocr_cache) > MAX_OCR_CACHE:
            _ocr_cache.clear()
        _ocr_cache[text] = _normalize(embedder.embed_query(text))
    return _ocr_cache[text]

def retrieve_similar_images(
        image_url: str, 
        owner_id: str,
    top_k: int = 5,
    min_score: float | None = None,
        ) -> List[Dict]:
    client  =  get_qdrant_client()

    emb = embed_image(image_url) 

    if emb["source"] in ["ocr","ocr_fallback"]:
        return []
    
    image_vector = _normalize(emb["vector"])

    owner_filter = Filter(
        must=[
            FieldCondition(
                key="owner_id",
                match=MatchValue(value=owner_id)
            )
        ]
    )

    ####################################################### Explantaion of client.qdrant_points ########################################################

                    # client.query_points is used to query the Qdrant collection for similar images
                    #You give it a vector → it finds the closest matching vectors stored in the collection

                    #     general Syntax
                    #     client.query_points(
                    #     collection_name: str,
                    #     query: list[float] | dict,
                    #     using: str | None = None,
                    #     query_filter: Filter | None = None,
                    #     limit: int = 10,
                    #     with_payload: bool | list[str] = False,
                    #     with_vector: bool | list[str] = False,
                    #     score_threshold: float | None = None,
                    #     offset: int | None = None
                    # )

    ####################################################### Explantaion of client.qdrant_points ########################################################

    result = client.query_points(
        collection_name = IMAGE_COLLECTION,
        query = image_vector,
        using = "image",
        query_filter = owner_filter,
        limit = top_k,
        with_payload = True
    )

    query_ocr = emb.get("ocr_text") or ""
    use_text = _good_ocr(query_ocr)
    text_embedder = _get_text_embedder() if use_text else None
    query_text_vec = _normalize(text_embedder.embed_query(query_ocr)) if text_embedder else None

    reranked = []
    for p in result.points:
        base_score = float(p.score)
        text_score = 0.0
        cand_text = p.payload.get("ocr_text")
        if text_embedder and _good_ocr(cand_text):
            cand_vec = _embed_cached(cand_text, text_embedder)
            text_score = _cosine(query_text_vec, cand_vec)
        combined = 0.75 * base_score + 0.25 * text_score if text_score > 0 else base_score

        reranked.append({
            "id": p.id,
            "score": base_score,
            "combined_score": combined,
            "image_url": p.payload.get("image_url"),
            "file_id": p.payload.get("file_id"),
            "ocr_text": p.payload.get("ocr_text"),
        })

    reranked.sort(key=lambda x: x["combined_score"], reverse=True)
    return reranked[:top_k]

# Equivalanet code to above return statement

    # output = []

    # for p in results.points:
    #     output.append({
    #          "id": p.id,
    #         "score": p.score,
    #         "image_url": p.payload.get("image_url"),
    #         "file_id": p.payload.get("file_id"),
    #         "ocr_text":p.payload.get("ocr_text"),
    #     })
    # return output










