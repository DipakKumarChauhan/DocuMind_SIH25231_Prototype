# from typing import List, Dict
# from qdrant_client.models import Filter, FieldCondition, MatchValue
# from app.db.qdrant_client import get_qdrant_client
# from app.embeddings.base import EmbeddingModel

# COLLECTION = "text_collection"

# def retrieve_text_chunks(
#         query: str,
#         owner_id:str,
#         embedder: EmbeddingModel,
#         top_k: int =5
# )-> List[Dict]:
#     client = get_qdrant_client()

#     query_vector = embedder.embed_query(query)

#     owner_filter = Filter(
#         must=[
#             FieldCondition(
#                 key = "owner_id",
#                 match= MatchValue(value= owner_id)
#             )
#         ]
#         )
    
#     results = client.search(
#         collection_name = COLLECTION,
#         query_vector = query_vector,
#         limit = top_k,
#         query_filter = owner_filter,
#         with_payload = True,
#         with_vectors = False,
#     )

#     hits = []
#     for res in results:
#         hits.append({
#             "id": res.id,
#             "score":res.score,
#             "text": res.payload.get("text"),
#             "metadata":res.payload,
#         })

#     #return hits    

# # New Chnge of filtering based on min score

#     # --- Dynamic score threshold ---
#     tokens = query.split()

#     if len(tokens) <= 2:
#         MIN_SCORE = 0.30
#     else:
#         MIN_SCORE = 0.38

#     filtered_hits = [h for h in hits if h["score"] >= MIN_SCORE]

#     # Fallback if all results disappear
#     if not filtered_hits:
#         return hits

#     return filtered_hits


################# New Change ####################

from typing import List, Dict, Any
from qdrant_client.models import Filter, FieldCondition, MatchValue, Prefetch, SparseVector
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.base import EmbeddingModel
from app.embeddings.sparse.tfidf import TfidfSparseEncoder

COLLECTION = "text_collection"

# RRF (Reciprocal Rank Fusion) constant
RRF_K = 60  # Standard RRF constant (higher = more weight to lower ranks)


# -------------------------------
# 🔍 Entity detection helper
# -------------------------------
def is_named_entity_query(query: str) -> bool:
    """Detect if query is likely a named entity (person, acronym, etc.)"""
    tokens = query.strip().split()
    return (
        1 <= len(tokens) <= 3
        and all(t[0].isupper() for t in tokens if t)
    )


def _normalize_score(score: Any) -> float | None:
    """Handle score normalization for hybrid search results"""
    if score is None:
        return None
    if isinstance(score, list):
        return max(score) if score else None
    return float(score)


def _reciprocal_rank_fusion(
    dense_results: List[Dict],
    sparse_results: List[Dict],
    k: int = RRF_K,
) -> List[Dict]:
    """
    Combine dense and sparse results using Reciprocal Rank Fusion (RRF).
    
    RRF formula: score(doc) = sum(1 / (k + rank_i))
    where rank_i is the rank in each result list (1-indexed)
    
    Args:
        dense_results: Results from dense vector search (sorted by score)
        sparse_results: Results from sparse vector search (sorted by score)
        k: RRF constant (default 60, standard value)
        
    Returns:
        List of results sorted by fused RRF score
    """
    # Build RRF scores by document ID
    rrf_scores = {}
    
    # Add dense ranks (1-indexed)
    for rank, result in enumerate(dense_results, start=1):
        doc_id = result["id"]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank))
    
    # Add sparse ranks (1-indexed)
    for rank, result in enumerate(sparse_results, start=1):
        doc_id = result["id"]
        rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + (1.0 / (k + rank))
    
    # Merge results with RRF scores
    all_results = {}
    for result in dense_results + sparse_results:
        doc_id = result["id"]
        if doc_id not in all_results:
            all_results[doc_id] = result.copy()
            all_results[doc_id]["rrf_score"] = rrf_scores[doc_id]
            all_results[doc_id]["original_score"] = result.get("score")
    
    # Sort by RRF score (descending)
    fused = sorted(
        all_results.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
    )
    
    # Use RRF score as the main score
    for result in fused:
        result["score"] = result["rrf_score"]
    
    return fused


# ==========================================
# OLD VERSION: Entity-routing search (kept for reference)
# ==========================================
# def retrieve_text_chunks_ROUTING(
#     query: str,
#     owner_id: str,
#     embedder: EmbeddingModel,
#     top_k: int = 5,
# ) -> List[Dict]:
#
#     if not query.strip():
#         return []
#
#     client = get_qdrant_client()
#     tfidf = TfidfSparseEncoder()
#
#     owner_filter = Filter(
#         must=[FieldCondition(key="owner_id", match=MatchValue(value=owner_id))]
#     )
#
#     entity_query = is_named_entity_query(query)
#
#     # 🔤 ENTITY / NAME SEARCH (sparse-only)
#     if entity_query and tfidf.is_fitted():
#         sparse_vec_dict = tfidf.encode(query)
#         sparse_vec = SparseVector(
#             indices=sparse_vec_dict["indices"],
#             values=sparse_vec_dict["values"]
#         )
#         result = client.query_points(
#             collection_name=COLLECTION,
#             query=sparse_vec,
#             using="sparse",
#             query_filter=owner_filter,
#             limit=top_k,
#             with_payload=True,
#             with_vectors=False,
#         )
#         MIN_SCORE = 0.08
#         results = result.points
#
#     # 🧠 CONCEPT / SEMANTIC SEARCH (dense-only)
#     else:
#         dense_vec = embedder.embed_query(query)
#         result = client.query_points(
#             collection_name=COLLECTION,
#             query=dense_vec,
#             using="dense",
#             query_filter=owner_filter,
#             limit=top_k,
#             with_payload=True,
#             with_vectors=False,
#         )
#         MIN_SCORE = 0.30 if len(query.split()) <= 2 else 0.38
#         results = result.points
#
#     hits = []
#     for r in results:
#         hits.append({
#             "id": r.id,
#             "score": float(r.score),
#             "text": r.payload.get("text"),
#             "metadata": r.payload,
#         })
#
#     filtered = [h for h in hits if h["score"] >= MIN_SCORE]
#     return filtered or hits


# ==========================================
# ✅ ACTIVE: Adaptive Hybrid Search
# ==========================================
def retrieve_text_chunks(
    query: str,
    owner_id: str,
    embedder: EmbeddingModel,
    top_k: int = 5,
) -> List[Dict]:
    """
    Simple hybrid search optimized for multimodal consistency.
    Uses dense vectors with optional sparse boost when available.
    Returns cosine scores (0.2-0.7) consistent with image/audio retrieval.
    """
    if not query.strip():
        return []

    client = get_qdrant_client()
    tfidf = TfidfSparseEncoder()

    owner_filter = Filter(
        must=[
            FieldCondition(
                key="owner_id",
                match=MatchValue(value=owner_id),
            )
        ]
    )

    dense_vec = embedder.embed_query(query)
    
    # Use sparse boost if TF-IDF is fitted, otherwise pure dense
    if tfidf.is_fitted():
        sparse_vec_dict = tfidf.encode(query)
        sparse_vec = SparseVector(
            indices=sparse_vec_dict["indices"],
            values=sparse_vec_dict["values"]
        )
        
        # Hybrid search with Qdrant's built-in fusion
        result = client.query_points(
            collection_name=COLLECTION,
            prefetch=[
                Prefetch(
                    query=dense_vec,
                    using="dense",
                    limit=top_k * 2,
                ),
                Prefetch(
                    query=sparse_vec,
                    using="sparse",
                    limit=top_k * 2,
                ),
            ],
            query=dense_vec,
            using="dense",
            query_filter=owner_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )
    else:
        # Dense-only fallback
        result = client.query_points(
            collection_name=COLLECTION,
            query=dense_vec,
            using="dense",
            query_filter=owner_filter,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

    hits = []
    for point in result.points:
        score = _normalize_score(point.score)
        hits.append({
            "id": point.id,
            "score": score,
            "text": point.payload.get("text"),
            "metadata": point.payload,
        })

    # Relaxed thresholds - consistent with image/audio retrieval
    # Shorter queries naturally have lower scores
    MIN_SCORE = 0.25 if len(query.split()) <= 2 else 0.28
    
    filtered = [h for h in hits if h["score"] is None or h["score"] >= MIN_SCORE]
    return filtered or hits


# ==========================================
# ARCHIVED: Pure Hybrid Search (kept for reference)
# ==========================================
# def retrieve_text_chunks_PURE_HYBRID(
#     query: str,
#     owner_id: str,
#     embedder: EmbeddingModel,
#     top_k: int = 5,
# ) -> List[Dict]:
#     """Pure hybrid: all queries use dense+sparse fusion"""
#     if not query.strip():
#         return []
#
#     client = get_qdrant_client()
#     tfidf = TfidfSparseEncoder()
#     dense_vec = embedder.embed_query(query)
#
#     owner_filter = Filter(
#         must=[FieldCondition(key="owner_id", match=MatchValue(value=owner_id))]
#     )
#
#     if tfidf.is_fitted():
#         sparse_vec_dict = tfidf.encode(query)
#         sparse_vec = SparseVector(
#             indices=sparse_vec_dict["indices"],
#             values=sparse_vec_dict["values"]
#         )
#         result = client.query_points(
#             collection_name=COLLECTION,
#             prefetch=[
#                 Prefetch(query=dense_vec, using="dense", limit=50),
#                 Prefetch(query=sparse_vec, using="sparse", limit=50),
#             ],
#             query=dense_vec,
#             using="dense",
#             query_filter=owner_filter,
#             limit=top_k,
#             with_payload=True,
#             with_vectors=False,
#         )
#     else:
#         result = client.query_points(
#             collection_name=COLLECTION,
#             query=dense_vec,
#             using="dense",
#             query_filter=owner_filter,
#             limit=top_k,
#             with_payload=True,
#             with_vectors=False,
#         )
#
#     hits = []
#     for point in result.points:
#         score = _normalize_score(point.score)
#         hits.append({
#             "id": point.id,
#             "score": score,
#             "text": point.payload.get("text"),
#             "metadata": point.payload,
#         })
#
#     MIN_SCORE = 0.30 if len(query.split()) <= 2 else 0.38
#     filtered = [h for h in hits if h["score"] is None or h["score"] >= MIN_SCORE]
#     return filtered or hits
