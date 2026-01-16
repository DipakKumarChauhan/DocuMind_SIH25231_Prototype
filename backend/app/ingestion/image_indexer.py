import uuid
from datetime import datetime
from qdrant_client.models import PointStruct
from app.db.qdrant_client import get_qdrant_client
from app.embeddings.hf_bge_m3 import HFBgeM3Embedder
from app.embeddings.image.orchestrator import embed_image

IMAGE_COLLECTION = "image_collection"

def index_image(
        image_url:str,
        owner_id:str,
        file_id:str,
        bbox:list | None = None,
):
    """
    Index a single image into Qdrant with both image and OCR text vectors.
    """

    client = get_qdrant_client()

    embedding_result = embed_image(image_url)   

    vector = embedding_result.get("vector")
    source = embedding_result.get("source")
    ocr_text = embedding_result.get("ocr_text")
    ocr_blocks = embedding_result.get("ocr_blocks")  # preserve bounding boxes for future use

    # Guard empty OCR fields
    if isinstance(ocr_text, str) and not ocr_text.strip():
        ocr_text = None
    if not ocr_blocks:
        ocr_blocks = None

    # Always store both vectors for maximum search flexibility
    vectors = {}
    
    if source in ("local", "remote"):
        # CLIP image vector (512-dim)
        vectors["image"] = vector
        # Also embed OCR text for text-based search (1024-dim)
        if ocr_text:
            text_embedder = HFBgeM3Embedder()
            vectors["ocr"] = text_embedder.embed_query(ocr_text)
    elif source in ("ocr", "ocr_fallback"):
        # OCR text vector only (1024-dim)
        vectors["ocr"] = vector
        # No image vector available in this mode
    else:
        # Default: image vector
        vectors["image"] = vector
        if ocr_text:
            text_embedder = HFBgeM3Embedder()
            vectors["ocr"] = text_embedder.embed_query(ocr_text)

    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=vectors,
        payload={
            "owner_id": owner_id,
            "image_url": image_url,
            "file_id": file_id,
            "ocr_text": ocr_text,
            "ocr_blocks": ocr_blocks,
            "bbox": bbox,
            "source": source,
            "created_at": datetime.utcnow().isoformat(),
        },
    )

    client.upsert(
        collection_name=IMAGE_COLLECTION,
        points=[point],
    )


