from typing import List, Dict
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.image.orchestrator import embed_image
from app.embeddings.image.clip_text import embed_text_clip
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.embeddings.sparse.tfidf import TfidfSparseEncoder

IMAGE_COLLECTIONS = "image_collection"
TEXT_COLLECTION = "text_collection"

def retrieve_images_from_text(
        query: str,
        owner_id: str,
        top_k:int = 5,
)-> List[Dict]:
    """
    Text-to-image search using CLIP text encoder (512-dim) to match image space.
    """
    client = get_qdrant_client()

    # Use CLIP text encoder for cross-modal search (same 512-dim space as images)
    dense_vec = embed_text_clip(query)

    owner_filter = Filter(
        must = [
            FieldCondition(
                key = "owner_id",
                match = MatchValue(value= owner_id)
            )
        ]
    )
    results = client.query_points(
        collection_name = IMAGE_COLLECTIONS,
        query = dense_vec,
        using = "image",
        query_filter = owner_filter,
        limit = top_k * 2,  # Get more candidates for filtering
        with_payload = True,
        with_vectors = False,
    )
    hits = []

    for p in results.points:
        hits.append({
            "id": p.id,
            "score": float(p.score),
            "image_url": p.payload["image_url"], # image_url is mandatory and if it doesnot exist then error will be thrown so we used [] not .get()
            "ocr_text": p.payload.get("ocr_text"),
            "file_id": p.payload["file_id"],
            "bbox": p.payload.get("bbox"), # bbox is optional so we used .get() method and if there is no bbox it will return None
        })

    # Filter by threshold - CLIP scores are naturally lower for cross-modal search
    # Adaptive threshold based on query length (longer queries = lower scores expected)
    query_words = len(query.split())
    if query_words <= 3:
        MIN_SCORE = 0.20  # Short queries
    elif query_words <= 8:
        MIN_SCORE = 0.18  # Medium queries
    else:
        MIN_SCORE = 0.15  # Long queries (like your 15-word example)
    
    filtered = [h for h in hits if h["score"] >= MIN_SCORE]
    
    # Return filtered results up to top_k, or all hits if nothing passes threshold
    return (filtered or hits)[:top_k]

def retrieve_image_from_image(
        image_url:str,
        owner_id:str,
        top_k: int =5,
) -> List[Dict]:
    
    client = get_qdrant_client()

    emb  =  embed_image(image_url)
    image_vec = emb["vector"]

    owner_filter = Filter(
        must = [
            FieldCondition(
                key = "owner_id",
                match = MatchValue(value= owner_id)
            )
        ]
    )

    results = client.query_points(
        collection_name = IMAGE_COLLECTIONS,
        query_vector = image_vec,
        using = "image",
        query_filter = owner_filter,
        limit = top_k,
        with_payload = True,
        with_vectors = False,
    )

    hits = []

    for p in results.points:
        hits.append({
            "id": p.id,
            "score": float(p.score),
            "image_url": p.payload["image_url"],
            "ocr_text": p.payload.get("ocr_text"),
            "file_id": p.payload["file_id"],
            "bbox": p.payload.get("bbox"),

        })

    return hits

