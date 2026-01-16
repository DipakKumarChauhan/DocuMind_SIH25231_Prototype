from qdrant_client.models import VectorParams, Distance, PayloadSchemaType, SparseVectorParams
from app.db.qdrant_client import get_qdrant_client

TEXT_VECTOR_SIZE = 1024 # example: BGE-base vector size
IMAGE_VECTOR_SIZE = 512 # example:CLIP vit-base-patch32 (confirmed in your tests)
AUDIO_VECTOR_SIZE = 1024 #512 # example: speech embeddings vector size

def create_collections():
    client = get_qdrant_client()

    existing = {
        col.name for col in client.get_collections().collections
    }

    if "text_collection" not in existing:
        client.create_collection(
            collection_name="text_collection",
            # vectors_config= VectorParams(
            #     size = TEXT_VECTOR_SIZE,
            #     distance= Distance.COSINE,
            # ),
            vectors_config = {
                "dense": VectorParams(
                    size= TEXT_VECTOR_SIZE,
                    distance= Distance.COSINE,
                ),},
                sparse_vectors_config = {"sparse": SparseVectorParams() 
                },
        )
        # Create payload index for owner_id to support filtering 
        # Added while implemeting retriever
        client.create_payload_index(
            collection_name="text_collection",
            field_name = "owner_id",
            field_schema = PayloadSchemaType.KEYWORD,
        )
    
    if "image_collection" not in existing:
        # Named vectors to separate modalities and avoid dimension conflicts:
        # - "image": 512-dim CLIP image/text space
        # - "ocr":   1024-dim BGE-M3 text space (OCR-derived)
        client.create_collection(
            collection_name="image_collection",
            vectors_config={
                "image": VectorParams(
                    size=IMAGE_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
                "ocr": VectorParams(
                    size=TEXT_VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            },
        )
        # Create payload index for owner_id to support filtering
        client.create_payload_index(
            collection_name="image_collection",
            field_name="owner_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    if "audio_collection" not in existing:
        client.create_collection(
            collection_name="audio_collection",
            vectors_config={
                "transcript": VectorParams(
                size=AUDIO_VECTOR_SIZE,
                distance=Distance.COSINE,
            )},
        )
        client.create_payload_index(
            collection_name="audio_collection",
            field_name="owner_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
