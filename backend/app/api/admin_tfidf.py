# Initializes the TF-IDF vocabulary by loading text documents from Qdrant,
# training the TF-IDF encoder on them, and preventing re-initialization if it’s already fitted.


from fastapi import APIRouter, Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.embeddings.sparse.tfidf import TfidfSparseEncoder
from app.db.qdrant_client import get_qdrant_client

router = APIRouter(prefix="/admin", tags=["Admin"])

COLLECTION = "text_collection"

@router.post("/bootstrap-tfidf")
def bootstrap_tfidf(
    current_user: User = Depends(get_current_user),
):
    # # --- Admin guard ---
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")

    tfidf = TfidfSparseEncoder()

    if tfidf.is_fitted():
        raise HTTPException(
            status_code=400,
            detail="TF-IDF vocabulary already initialized",
        )

    # --- Load corpus from Qdrant ---
    client = get_qdrant_client()
    
        # Scroll through all points in the collection
        # Scroll retuns two things : points → the list of documents returned , next_page_token → a continuation token (used for pagination) in format (points, next_page_token)
        
    points, _ = client.scroll( # scroll means to iterate through all the items in the collection

        collection_name=COLLECTION,
        limit=10000,  # Adjust based on your corpus size
        with_payload=True, #include the stored text metadata
        with_vectors=False, #don’t return their vector embeddings (saves memory)
    )

        # Note here TF-IDF is  Trained on only first batch of 10,000 items so if sorpus has 50,000 items only first 10,000 are used to build vocabulary SO if it increases then we have to change this 

        # if No items found in the collection then raise error
    if not points: 
        raise HTTPException(
            status_code=400,
            detail="No text chunks found to build vocabulary",
        )

    texts = [point.payload.get("text", "") for point in points if point.payload.get("text")]

    # --- Fit TF-IDF ---
    tfidf.fit(texts)

    return {
        "status": "success",
        "message": "TF-IDF vocabulary initialized",
        "num_documents": len(texts),
    }
