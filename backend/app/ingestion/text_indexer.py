# from typing import List

# from sklearn import logger
# from qdrant_client.models import PointStruct
# from app.db.qdrant_client import get_qdrant_client
# from app.embeddings.base import EmbeddingModel
# from app.embeddings.sparse.tfidf import TfidfSparseEncoder



# COLLECTION = "text_collection"

# def index_text_chunks(
#     chunks: List[dict],
#     embedder: EmbeddingModel,
# ) -> int:
#     client = get_qdrant_client()

#     tfidf = TfidfSparseEncoder()
#     # ORIGINAL VERSION: Strict TF-IDF requirement (commented out to allow initial indexing)
#     # if not tfidf.is_fitted():
#     #     raise RuntimeError(
#     #     "TF-IDF vocabulary not initialized. Run /admin/bootstrap-tfidf first."
#     # )
    
#     # NEW VERSION: Check if TF-IDF is available, use it if fitted, skip if not
#     use_sparse = tfidf.is_fitted()

#     texts = [c["text"] for c in chunks]
#     vectors = embedder.embed_documents(texts)

#     if len(vectors) != len(chunks):
#         raise RuntimeError("Embedding count mismatch")
    
#     points = []
#     for ch, vec in zip(chunks, vectors):
#         # ORIGINAL VERSION: Always requires sparse vector (commented out)
#         # sparse_vec = tfidf.encode(ch["text"])
#         # vector={
#         #     "dense": vec,
#         #     "sparse": sparse_vec,
#         # },
        
#         # NEW VERSION: Conditional sparse vector based on TF-IDF availability
#         if use_sparse:
#             sparse_vec = tfidf.encode(ch["text"])
#         else:
#             # ATTEMPTED FIX 1: Empty dict (commented - didn't work)
#             # sparse_vec = {}
            
#             # ATTEMPTED FIX 2: Proper Qdrant sparse format with empty indices/values
#             sparse_vec = {
#                 "indices": [],
#                 "values": []
#             }
        
#         vector_data = {
#             "dense": vec,
#             "sparse": sparse_vec,
#         }

#         points.append(
#             PointStruct(
#                 id=ch["id"],

#                 # Older version
#                 # vector={
#         #     "dense": vec,
#         #     "sparse": sparse_vec,
#         # },

#                 vector=vector_data,
#                # payload=ch["metadata"],
#                # New changes
#                 payload = {
#                     **ch["metadata"],
#                     "text": ch["text"],
#                 }
#             )
#         )

#     client.upsert(collection_name=COLLECTION, points=points, wait=True)
#     logger.info(f"Indexed {len(points)} hybrid chunks")

#     return len(points)


############## A different approach to handle sparse vectors ##############

from typing import List, Dict
from qdrant_client.models import PointStruct,Filter, FieldCondition, MatchValue, Prefetch
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.base import EmbeddingModel
from app.embeddings.sparse.tfidf import TfidfSparseEncoder


COLLECTION = "text_collection"

def index_text_chunks(
    chunks: List[dict],
    embedder: EmbeddingModel,
) -> int:
    client = get_qdrant_client()
    tfidf = TfidfSparseEncoder()

    texts = [c["text"] for c in chunks]
    dense_vectors = embedder.embed_documents(texts)

    if len(dense_vectors) != len(chunks):
        raise RuntimeError("Embedding count mismatch")

    use_sparse = tfidf.is_fitted()

    points = []
    for ch, dense_vec in zip(chunks, dense_vectors):
        vector_data = {"dense": dense_vec}

        if use_sparse:
            vector_data["sparse"] = tfidf.encode(ch["text"])

        points.append(
            PointStruct(
                id=ch["id"],
                vector=vector_data,
                payload={
                    **ch["metadata"],
                    "text": ch["text"],
                },
            )
        )

    client.upsert(collection_name=COLLECTION, points=points, wait=True)
    return len(points)




# def retrieve_text_chunks(
#     query: str,
#     owner_id: str,
#     embedder: EmbeddingModel,
#     top_k: int = 5,
# ) -> List[Dict]:

#     if not query.strip():
#         return []

#     client = get_qdrant_client()

#     tfidf = TfidfSparseEncoder()
#     if not tfidf.is_fitted():
#         raise RuntimeError("TF-IDF vocabulary not initialized")

#     dense_vec = embedder.embed_query(query)
#     sparse_vec = tfidf.encode(query)

#     owner_filter = Filter(
#         must=[FieldCondition(key="owner_id", match=MatchValue(value=owner_id))]
#     )

#     results = client.search(
#         collection_name=COLLECTION,
#         prefetch=[
#             Prefetch(query=dense_vec, using="dense", limit=50),
#             Prefetch(query=sparse_vec, using="sparse", limit=50),
#         ],
#         query=dense_vec,
#         using="dense",
#         limit=top_k,
#         filter=owner_filter,
#         with_payload=True,
#         with_vectors=False,
#     )

#     hits = [
#         {
#             "id": r.id,
#             "score": r.score,
#             "text": r.payload.get("text"),
#             "metadata": r.payload,
#         }
#         for r in results
#     ]

#     MIN_SCORE = 0.30 if len(query.split()) <= 2 else 0.38
#     return [h for h in hits if h["score"] >= MIN_SCORE] or hits
