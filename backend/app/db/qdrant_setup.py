from qdrant_client import QdrantClient, PayloadSchemaType
from qdrant_client.models import VectorParams, Distance
from app.config import settings

def setup_qdrant_collections():
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    collections = {c.name for c in client.get_collections().collections}

    if "text_collection" not in collections:
        client.create_collection(
            collection_name="text_collection",
            vectors_config=VectorParams(
                size=1024,
                distance=Distance.COSINE,
            ),
        )
        # Create payload index for owner_id to support filtering 
        # Added while implemeting retriever
        client.create_payload_index(
            collection_name="text_collection",
            field_name = "owner_id",
            field_schema = PayloadSchemaType.KEYWORD,
        )
